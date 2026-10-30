"""Testes da API HTTP, percorrendo o fluxo completo do aplicativo.

A API é opcional (extra ``api``): sem FastAPI instalado, o módulo inteiro é
pulado em vez de quebrar a suíte.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

fastapi = pytest.importorskip("fastapi", reason="requer o extra 'api'")
from fastapi.testclient import TestClient  # noqa: E402

from planejador.api.app import _sessao, app  # noqa: E402
from planejador.database.connection import Base  # noqa: E402
from planejador.database.seed import semear  # noqa: E402


@pytest.fixture
def cliente() -> Iterator[TestClient]:
    """Cliente HTTP ligado a um SQLite em memória já semeado.

    Substitui a dependência de sessão e desliga o ``lifespan``, para os testes
    não tocarem no banco real nem dependerem do bootstrap.

    O ``StaticPool`` é essencial aqui: o ``TestClient`` atende as requisições em
    outra thread, e o pool padrão do SQLite em memória daria a essa thread uma
    conexão nova — ou seja, um banco vazio. Com pool estático, todas as threads
    compartilham a mesma conexão e enxergam as tabelas semeadas.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    sessao = factory()
    semear(sessao)
    sessao.commit()

    def _sessao_de_teste() -> Iterator[Session]:
        yield sessao

    app.dependency_overrides[_sessao] = _sessao_de_teste
    try:
        # sem context manager: não dispara o lifespan (que criaria o banco real)
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        sessao.close()
        Base.metadata.drop_all(engine)


def _id_do_protocolo(cliente: TestClient, tipo: str) -> int:
    protocolos = cliente.get("/protocolos").json()
    return next(p["id"] for p in protocolos if p["tipo"] == tipo)


def test_listar_protocolos(cliente):
    resp = cliente.get("/protocolos")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_criar_plano_completo(cliente):
    protocolo_id = _id_do_protocolo(cliente, "microplaca")
    resp = cliente.post(
        "/planos",
        json={
            "protocolo_id": protocolo_id,
            "n_amostras": 8,
            "n_replicatas": 3,
            "n_controles": 2,
            "conc_inicial": 10.0,
            "conc_final": 1.0,
            "volume_final": 100.0,
        },
    )
    assert resp.status_code == 200
    plano = resp.json()
    assert plano["microplaca"]["pocos_totais"] == 26
    assert plano["tubos"]["tubos_totais"] == 27
    assert plano["preparo"]["diluicao"]["volume_alicota"] == 10.0
    assert plano["descricao"]
    assert plano["procedimento"]


def test_criar_plano_protocolo_inexistente(cliente):
    resp = cliente.post(
        "/planos", json={"protocolo_id": 999, "n_amostras": 1}
    )
    assert resp.status_code == 404


def test_criar_plano_entrada_invalida_traz_dica(cliente):
    protocolo_id = _id_do_protocolo(cliente, "preparo_solucao")
    resp = cliente.post(
        "/planos",
        json={
            "protocolo_id": protocolo_id,
            "n_amostras": 1,
            "conc_final": 5.0,  # sem volume: erro de domínio com dica
        },
    )
    assert resp.status_code == 400
    assert "dica" in resp.json()["detail"]


def test_amostras_zero_rejeitado_pelo_schema(cliente):
    protocolo_id = _id_do_protocolo(cliente, "preparo_solucao")
    resp = cliente.post(
        "/planos", json={"protocolo_id": protocolo_id, "n_amostras": 0}
    )
    assert resp.status_code == 422


def test_fluxo_experimento_ate_estatistica(cliente):
    protocolo_id = _id_do_protocolo(cliente, "preparo_solucao")

    criado = cliente.post(
        "/experimentos",
        json={
            "protocolo_id": protocolo_id,
            "titulo": "Ensaio via API",
            "medicoes": {"controle": [1.0, 1.1, 0.9]},
        },
    )
    assert criado.status_code == 201
    exp_id = criado.json()["id"]

    adicionadas = cliente.post(
        f"/experimentos/{exp_id}/medicoes",
        json={"medicoes": {"tratamento": [5.0, 5.2, 4.8]}},
    )
    assert adicionadas.status_code == 201
    assert adicionadas.json()["n_medicoes"] == 6

    detalhe = cliente.get(f"/experimentos/{exp_id}").json()
    assert len(detalhe["medicoes"]) == 6
    assert len(detalhe["resumo"]) == 2

    estat = cliente.get(f"/experimentos/{exp_id}/estatistica").json()
    assert estat["teste_t"]["significativo"] is True
    assert len(estat["tabela_medicoes"]) == 6


def test_listar_experimentos_filtrado(cliente):
    protocolo_id = _id_do_protocolo(cliente, "preparo_solucao")
    cliente.post(
        "/experimentos",
        json={"protocolo_id": protocolo_id, "titulo": "Filtrado"},
    )
    resp = cliente.get("/experimentos", params={"protocolo_id": protocolo_id})
    assert resp.status_code == 200
    assert [e["titulo"] for e in resp.json()] == ["Filtrado"]


def test_estatistica_sem_medicoes_erro(cliente):
    protocolo_id = _id_do_protocolo(cliente, "preparo_solucao")
    exp_id = cliente.post(
        "/experimentos",
        json={"protocolo_id": protocolo_id, "titulo": "Sem dados"},
    ).json()["id"]
    resp = cliente.get(f"/experimentos/{exp_id}/estatistica")
    assert resp.status_code == 400
    assert "não possui medições" in resp.json()["detail"]["mensagem"]


def test_experimento_inexistente(cliente):
    assert cliente.get("/experimentos/999").status_code == 404


def test_exportacao_csv(cliente, tmp_path):
    protocolo_id = _id_do_protocolo(cliente, "preparo_solucao")
    exp_id = cliente.post(
        "/experimentos",
        json={
            "protocolo_id": protocolo_id,
            "titulo": "Exportável",
            "medicoes": {"controle": [1.0, 1.2], "tratamento": [2.0, 2.4]},
        },
    ).json()["id"]

    resp = cliente.post(
        f"/experimentos/{exp_id}/exportacoes", json={"destino": str(tmp_path)}
    )
    assert resp.status_code == 200
    assert len(list(tmp_path.glob("*.csv"))) == 2
