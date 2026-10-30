"""Testes de integração da camada de serviços (core + banco em memória)."""

from __future__ import annotations

import math

import pytest

from planejador.core.exceptions import EntradaInvalida
from planejador.database import repositories as repo
from planejador.database.seed import semear
from planejador.services import (
    analisar_experimento,
    analisar_grupos,
    gerar_plano,
)


def test_gerar_plano_com_seed(session):
    semear(session)
    protocolos = repo.listar_protocolos(session)
    microplaca = next(p for p in protocolos if p.tipo == "microplaca")

    plano = gerar_plano(
        session,
        protocolo_id=microplaca.id,
        n_amostras=8,
        n_replicatas=3,
        n_controles=2,
    )
    assert plano.microplaca is not None
    assert plano.microplaca.pocos_totais == 26
    # 26 reações; caldo base 0,2 -> total 5,2
    caldo = next(r for r in plano.reagentes if "Caldo" in r.nome)
    assert math.isclose(caldo.quantidade_total, 26 * 0.2)


def test_plano_como_dict_serializavel(session):
    semear(session)
    prot = repo.listar_protocolos(session)[0]
    plano = gerar_plano(session, prot.id, n_amostras=5)
    d = plano.como_dict()
    assert isinstance(d, dict)
    assert "reagentes" in d and isinstance(d["reagentes"], list)


def test_analisar_grupos_dois_grupos_faz_teste_t():
    rel = analisar_grupos(
        {"controle": [1.0, 2.0, 3.0], "tratamento": [10.0, 11.0, 12.0]}
    )
    assert rel["teste_t"] is not None
    assert rel["anova"] is None
    assert rel["teste_t"]["significativo"] is True


def test_analisar_grupos_tres_grupos_faz_anova():
    rel = analisar_grupos(
        {"a": [1.0, 2.0, 3.0], "b": [1.1, 2.1, 3.1], "c": [1.2, 2.2, 3.2]}
    )
    assert rel["anova"] is not None
    assert rel["teste_t"] is None


def test_analisar_experimento_persistido(session):
    prot = repo.criar_protocolo(session, "P", "preparo_solucao")
    exp = repo.criar_experimento(session, prot.id, "E1")
    for v in (1.0, 2.0, 3.0):
        repo.registrar_medicao(session, exp.id, "controle", v)
    for v in (10.0, 11.0, 12.0):
        repo.registrar_medicao(session, exp.id, "tratamento", v)

    rel = analisar_experimento(session, exp.id)
    assert rel["teste_t"] is not None
    assert set(rel["resumos"].keys()) == {"controle", "tratamento"}


def test_plano_inclui_tubos_e_procedimento(session):
    semear(session)
    prot = repo.listar_protocolos(session)[0]
    plano = gerar_plano(session, prot.id, n_amostras=4, n_replicatas=2)
    # 4 × 2 = 8 tubos de amostra + 0 controles + 1 de preparo
    assert plano.tubos is not None
    assert plano.tubos.tubos_totais == 9
    assert plano.descricao  # resumo do protocolo veio do banco
    assert plano.procedimento
    assert any("Registrar as medições" in p for p in plano.procedimento)


def test_plano_preparo_por_diluicao(session):
    semear(session)
    prot = repo.listar_protocolos(session)[0]
    plano = gerar_plano(
        session,
        prot.id,
        n_amostras=2,
        conc_inicial=10.0,
        conc_final=1.0,
        volume_final=100.0,
    )
    assert plano.preparo is not None
    assert plano.preparo.diluicao is not None
    assert math.isclose(plano.preparo.diluicao.volume_alicota, 10.0)
    assert math.isclose(plano.preparo.diluicao.volume_diluente, 90.0)
    assert plano.preparo.massa_soluto is None
    assert any("solução-mãe" in p for p in plano.procedimento)


def test_plano_preparo_a_partir_do_solido(session):
    semear(session)
    prot = repo.listar_protocolos(session)[0]
    plano = gerar_plano(
        session, prot.id, n_amostras=1, conc_final=9.0, volume_final=1.0
    )
    assert plano.preparo is not None
    assert plano.preparo.diluicao is None
    assert math.isclose(plano.preparo.massa_soluto, 9.0)
    assert any("pesar" in p for p in plano.procedimento)


def test_plano_volume_derivado_por_reacao(session):
    semear(session)
    prot = repo.listar_protocolos(session)[0]
    # 3 amostras × 2 replicatas + 1 controle = 7 reações × 2 mL × 1,10 = 15,4
    plano = gerar_plano(
        session,
        prot.id,
        n_amostras=3,
        n_replicatas=2,
        n_controles=1,
        excesso_percentual=10.0,
        conc_final=5.0,
        volume_por_reacao=2.0,
    )
    assert plano.n_reacoes == 7
    assert plano.preparo is not None
    assert math.isclose(plano.preparo.volume_final, 15.4)


def test_plano_serie_de_diluicao_multiplica_tubos(session):
    semear(session)
    prot = repo.listar_protocolos(session)[0]
    plano = gerar_plano(
        session,
        prot.id,
        n_amostras=2,
        conc_final=100.0,
        volume_final=10.0,
        fator_serie=10.0,
        n_pontos_serie=4,
    )
    assert plano.preparo is not None
    assert plano.preparo.serie_diluicao == [100.0, 10.0, 1.0, 0.1]
    # 2 amostras × 1 replicata × 4 pontos = 8, + 4 tubos de preparo
    assert plano.tubos is not None
    assert plano.tubos.tubos_totais == 12


def test_plano_serie_de_diluicao_multiplica_pocos(session):
    """A placa deve escalar com a série, igual aos tubos."""
    semear(session)
    microplaca = next(
        p for p in repo.listar_protocolos(session) if p.tipo == "microplaca"
    )
    plano = gerar_plano(
        session,
        microplaca.id,
        n_amostras=8,
        n_replicatas=3,
        n_controles=2,
        conc_final=100.0,
        volume_final=10.0,
        fator_serie=2.0,
        n_pontos_serie=3,
    )
    assert plano.microplaca is not None
    # 8 × 3 × 3 = 72 poços de amostra; 2 × 3 = 6 de controle
    assert plano.microplaca.pocos_amostras == 72
    assert plano.microplaca.pocos_controles == 6
    assert plano.microplaca.pocos_totais == 78
    # tubos e poços contam as amostras da mesma forma
    assert plano.tubos is not None
    assert plano.microplaca.pocos_amostras == plano.tubos.tubos_amostras


def test_plano_pocos_por_placa_nao_e_confundido_com_pontos(session):
    """Protege a ordem dos argumentos de planejar_microplaca."""
    semear(session)
    microplaca = next(
        p for p in repo.listar_protocolos(session) if p.tipo == "microplaca"
    )
    plano = gerar_plano(
        session, microplaca.id, n_amostras=8, n_replicatas=3, pocos_por_placa=24
    )
    assert plano.microplaca is not None
    assert plano.microplaca.pocos_por_placa == 24
    assert plano.microplaca.n_pontos_diluicao == 1
    # 24 poços em placas de 24 -> exatamente 1 placa
    assert plano.microplaca.pocos_totais == 24
    assert plano.microplaca.placas_necessarias == 1


def test_plano_concentracao_sem_volume_erro(session):
    semear(session)
    prot = repo.listar_protocolos(session)[0]
    with pytest.raises(EntradaInvalida, match="sem volume"):
        gerar_plano(session, prot.id, n_amostras=1, conc_final=5.0)


def test_plano_sem_concentracao_nao_traz_preparo(session):
    semear(session)
    prot = repo.listar_protocolos(session)[0]
    plano = gerar_plano(session, prot.id, n_amostras=1)
    assert plano.preparo is None
    assert plano.como_dict()["preparo"] is None


def test_plano_como_dict_tem_todas_as_secoes(session):
    semear(session)
    prot = next(
        p for p in repo.listar_protocolos(session) if p.tipo == "microplaca"
    )
    plano = gerar_plano(
        session,
        prot.id,
        n_amostras=8,
        n_replicatas=3,
        n_controles=2,
        conc_inicial=10.0,
        conc_final=2.0,
        volume_final=50.0,
    )
    d = plano.como_dict()
    esperadas = {
        "protocolo",
        "tipo",
        "descricao",
        "n_reacoes",
        "reagentes",
        "materiais",
        "preparo",
        "tubos",
        "microplaca",
        "procedimento",
    }
    assert esperadas <= set(d)
    assert d["microplaca"]["pocos_totais"] == 26
    assert isinstance(d["procedimento"], list) and d["procedimento"]


def test_analise_traz_tabelas_estruturadas():
    rel = analisar_grupos(
        {"controle": [1.0, 2.0, 3.0], "tratamento": [10.0, 11.0, 12.0]}
    )
    assert len(rel["tabela_medicoes"]) == 6
    assert {linha["grupo"] for linha in rel["tabela_resumo"]} == {
        "controle",
        "tratamento",
    }
