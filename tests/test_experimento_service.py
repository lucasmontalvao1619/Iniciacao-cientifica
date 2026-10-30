"""Testes do serviço de experimentos (entrada de dados vinda da bancada)."""

from __future__ import annotations

import math

import pytest

from planejador.core.exceptions import EntradaInvalida, RegistroNaoEncontrado
from planejador.database import repositories as repo
from planejador.database.seed import semear
from planejador.services import (
    adicionar_medicoes,
    analisar_experimento,
    criar_experimento,
    exportar_experimento_csv,
    listar_experimentos,
    listar_protocolos,
    obter_experimento,
)


@pytest.fixture
def protocolo(session):
    """Um protocolo simples para pendurar os experimentos dos testes."""
    return repo.criar_protocolo(session, "Ensaio base", "preparo_solucao")


def test_listar_protocolos_traz_descricao(session):
    semear(session)
    protocolos = listar_protocolos(session)
    assert len(protocolos) == 2
    assert all(
        {"id", "nome", "tipo", "descricao"} <= set(p) for p in protocolos
    )
    assert any(p["descricao"] for p in protocolos)


def test_criar_experimento_com_medicoes(session, protocolo):
    exp = criar_experimento(
        session,
        protocolo_id=protocolo.id,
        titulo="Ensaio 12/08",
        observacoes="leitura a 600 nm",
        medicoes={"controle": [1.0, 1.2], "tratamento": [2.0, 2.4]},
    )
    assert exp["n_medicoes"] == 4
    assert exp["protocolo"] == "Ensaio base"
    assert exp["observacoes"] == "leitura a 600 nm"
    assert len(exp["medicoes"]) == 4
    assert len(exp["resumo"]) == 2


def test_criar_experimento_sem_medicoes_tabelas_vazias(session, protocolo):
    exp = criar_experimento(
        session, protocolo_id=protocolo.id, titulo="Só planejado"
    )
    assert exp["n_medicoes"] == 0
    assert exp["medicoes"] == []
    assert exp["resumo"] == []


def test_criar_experimento_titulo_vazio_erro(session, protocolo):
    with pytest.raises(EntradaInvalida, match="título"):
        criar_experimento(session, protocolo_id=protocolo.id, titulo="   ")


def test_criar_experimento_protocolo_inexistente(session):
    with pytest.raises(RegistroNaoEncontrado):
        criar_experimento(session, protocolo_id=999, titulo="X")


def test_adicionar_medicoes_acumula(session, protocolo):
    exp = criar_experimento(
        session,
        protocolo_id=protocolo.id,
        titulo="Em tandas",
        medicoes={"controle": [1.0]},
    )
    atualizado = adicionar_medicoes(
        session, exp["id"], {"controle": [1.4], "tratamento": [3.0]}
    )
    assert atualizado["grupos"]["controle"] == [1.0, 1.4]
    assert atualizado["n_medicoes"] == 3


def test_adicionar_medicoes_lote_vazio_erro(session, protocolo):
    exp = criar_experimento(
        session, protocolo_id=protocolo.id, titulo="Vazio"
    )
    with pytest.raises(EntradaInvalida, match="Nenhuma medição"):
        adicionar_medicoes(session, exp["id"], {})
    with pytest.raises(EntradaInvalida, match="sem nenhuma medição"):
        adicionar_medicoes(session, exp["id"], {"controle": []})


def test_obter_experimento_inexistente(session):
    with pytest.raises(RegistroNaoEncontrado):
        obter_experimento(session, 999)


def test_listar_experimentos_mais_recente_primeiro(session, protocolo):
    criar_experimento(session, protocolo_id=protocolo.id, titulo="Primeiro")
    criar_experimento(session, protocolo_id=protocolo.id, titulo="Segundo")
    listagem = listar_experimentos(session)
    assert [e["titulo"] for e in listagem] == ["Segundo", "Primeiro"]


def test_fluxo_completo_ate_estatistica(session, protocolo):
    """Da criação do experimento até o teste t, como no fluxo do aplicativo."""
    exp = criar_experimento(
        session,
        protocolo_id=protocolo.id,
        titulo="Fluxo completo",
        medicoes={
            "controle": [1.0, 1.1, 0.9],
            "tratamento": [5.0, 5.2, 4.8],
        },
    )
    relatorio = analisar_experimento(session, exp["id"])
    assert relatorio["teste_t"] is not None
    assert relatorio["teste_t"]["significativo"] is True
    assert len(relatorio["tabela_medicoes"]) == 6
    assert len(relatorio["tabela_resumo"]) == 2
    controle = next(
        linha
        for linha in relatorio["tabela_resumo"]
        if linha["grupo"] == "controle"
    )
    assert math.isclose(controle["media"], 1.0)


def test_exportar_experimento_csv(session, protocolo, tmp_path):
    exp = criar_experimento(
        session,
        protocolo_id=protocolo.id,
        titulo="Para exportar",
        medicoes={"controle": [1.0, 1.2], "tratamento": [2.0, 2.4]},
    )
    caminhos = exportar_experimento_csv(session, exp["id"], tmp_path)
    assert set(caminhos) == {"medicoes", "resumo"}
    for caminho in caminhos.values():
        assert (tmp_path / caminho.split("/")[-1]).exists()


def test_exportar_experimento_sem_medicoes_erro(session, protocolo, tmp_path):
    exp = criar_experimento(
        session, protocolo_id=protocolo.id, titulo="Sem dados"
    )
    with pytest.raises(EntradaInvalida, match="não possui medições"):
        exportar_experimento_csv(session, exp["id"], tmp_path)
