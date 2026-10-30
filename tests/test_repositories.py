"""Testes da camada de repositórios (banco em memória)."""

from __future__ import annotations

import pytest

from planejador.core.exceptions import RegistroNaoEncontrado
from planejador.database import repositories as repo


def test_criar_e_listar_reagente(session):
    repo.criar_reagente(session, "NaCl", "g")
    reagentes = repo.listar_reagentes(session)
    assert len(reagentes) == 1
    assert reagentes[0].nome == "NaCl"


def test_obter_protocolo_inexistente(session):
    with pytest.raises(RegistroNaoEncontrado):
        repo.obter_protocolo(session, 999)


def test_vinculos_e_medicoes_por_grupo(session):
    prot = repo.criar_protocolo(session, "Teste", "preparo_solucao")
    reag = repo.criar_reagente(session, "Água", "mL")
    repo.vincular_reagente(session, prot.id, reag.id, 100.0)

    exp = repo.criar_experimento(session, prot.id, "Ensaio 1")
    repo.registrar_medicao(session, exp.id, "controle", 1.0)
    repo.registrar_medicao(session, exp.id, "controle", 1.2)
    repo.registrar_medicao(session, exp.id, "tratamento", 2.0)

    grupos = repo.medicoes_por_grupo(session, exp.id)
    assert set(grupos.keys()) == {"controle", "tratamento"}
    assert grupos["controle"] == [1.0, 1.2]


def test_registrar_medicoes_em_lote(session):
    prot = repo.criar_protocolo(session, "P lote", "preparo_solucao")
    exp = repo.criar_experimento(session, prot.id, "Ensaio lote")
    criadas = repo.registrar_medicoes(
        session, exp.id, {"controle": [1.0, 1.2], "tratamento": [2.0]}
    )
    assert len(criadas) == 3
    grupos = repo.medicoes_por_grupo(session, exp.id)
    assert grupos["controle"] == [1.0, 1.2]
    assert grupos["tratamento"] == [2.0]


def test_registrar_medicoes_experimento_inexistente(session):
    with pytest.raises(RegistroNaoEncontrado):
        repo.registrar_medicoes(session, 999, {"controle": [1.0]})


def test_obter_experimento_inexistente(session):
    with pytest.raises(RegistroNaoEncontrado, match="Experimento"):
        repo.obter_experimento(session, 999)


def test_listar_experimentos_filtra_por_protocolo(session):
    p1 = repo.criar_protocolo(session, "P1 lista", "preparo_solucao")
    p2 = repo.criar_protocolo(session, "P2 lista", "microplaca")
    repo.criar_experimento(session, p1.id, "E de P1")
    repo.criar_experimento(session, p2.id, "E de P2")

    assert len(repo.listar_experimentos(session)) == 2
    so_p1 = repo.listar_experimentos(session, protocolo_id=p1.id)
    assert [e.titulo for e in so_p1] == ["E de P1"]
