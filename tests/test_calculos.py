"""Testes dos cálculos operacionais, com valores conferidos manualmente."""

from __future__ import annotations

import math

import pytest

from planejador.core import calculos
from planejador.core.exceptions import EntradaInvalida


def test_diluicao_valores_conferidos():
    # C1·V1 = C2·V2 -> V1 = C2·V2/C1 = 1·100/10 = 10
    r = calculos.preparar_diluicao(10.0, 1.0, 100.0)
    assert math.isclose(r.volume_alicota, 10.0)
    assert math.isclose(r.volume_diluente, 90.0)
    assert math.isclose(r.fator_diluicao, 10.0)


def test_diluicao_final_maior_que_inicial_erro():
    with pytest.raises(EntradaInvalida, match="maior que a inicial"):
        calculos.preparar_diluicao(1.0, 10.0, 100.0)


def test_diluicao_valor_negativo_erro():
    with pytest.raises(EntradaInvalida):
        calculos.preparar_diluicao(10.0, 1.0, -5.0)


def test_diluicao_seriada():
    assert calculos.diluicao_seriada(100.0, 10.0, 4) == [100.0, 10.0, 1.0, 0.1]


def test_diluicao_seriada_fator_invalido():
    with pytest.raises(EntradaInvalida):
        calculos.diluicao_seriada(100.0, 1.0, 3)


def test_massa_de_soluto():
    assert math.isclose(calculos.massa_de_soluto(9.0, 1.0), 9.0)


def test_escalonar_com_excesso():
    # 2 por reação × 10 reações × 1,10 (10% excesso) = 22
    assert math.isclose(calculos.escalonar_quantidade(2.0, 10, 10.0), 22.0)


def test_escalonar_sem_excesso():
    assert math.isclose(calculos.escalonar_quantidade(2.5, 4), 10.0)


def test_microplaca_uma_placa():
    p = calculos.planejar_microplaca(8, 3, 2)
    assert p.pocos_amostras == 24
    assert p.pocos_totais == 26
    assert p.placas_necessarias == 1


def test_microplaca_duas_placas():
    # 40 amostras × 3 = 120 poços -> 2 placas de 96
    p = calculos.planejar_microplaca(40, 3, 0)
    assert p.pocos_totais == 120
    assert p.placas_necessarias == 2


def test_microplaca_amostra_invalida():
    with pytest.raises(EntradaInvalida):
        calculos.planejar_microplaca(0, 3, 0)


def test_microplaca_com_serie_multiplica_pontos():
    # Dose-resposta: cada amostra ocupa um poço por replicata E por ponto.
    # amostras 8×3×3 = 72; controles 2×3 = 6 -> 78 poços, 1 placa de 96.
    p = calculos.planejar_microplaca(8, 3, 2, n_pontos_diluicao=3)
    assert p.pocos_amostras == 72
    assert p.pocos_controles == 6
    assert p.pocos_totais == 78
    assert p.placas_necessarias == 1
    assert p.n_pontos_diluicao == 3


def test_microplaca_serie_transborda_para_segunda_placa():
    # 8×3×5 = 120 poços de amostra + 2×5 = 10 de controle -> 130 -> 2 placas
    p = calculos.planejar_microplaca(8, 3, 2, n_pontos_diluicao=5)
    assert p.pocos_totais == 130
    assert p.placas_necessarias == 2


def test_microplaca_um_ponto_equivale_a_sem_serie():
    sem = calculos.planejar_microplaca(8, 3, 2)
    com_um = calculos.planejar_microplaca(8, 3, 2, n_pontos_diluicao=1)
    assert sem == com_um


def test_microplaca_pontos_invalidos():
    with pytest.raises(EntradaInvalida, match="ao menos 1 ponto"):
        calculos.planejar_microplaca(1, 1, 0, n_pontos_diluicao=0)
    with pytest.raises(EntradaInvalida):
        calculos.planejar_microplaca(1, 1, 0, pocos_por_placa=0)


def test_microplaca_e_tubos_concordam_na_contagem_de_amostras():
    """Poços e tubos devem escalar igual — foi a origem da divergência."""
    for pontos in (1, 2, 3, 4):
        p = calculos.planejar_microplaca(8, 3, 2, n_pontos_diluicao=pontos)
        t = calculos.planejar_tubos(8, 3, 2, n_pontos_diluicao=pontos)
        assert p.pocos_amostras == t.tubos_amostras
        assert p.pocos_controles == t.tubos_controles


def test_tubos_sem_serie_valores_conferidos():
    # 8 amostras × 3 replicatas = 24 tubos; + 2 controles + 1 de preparo = 27
    t = calculos.planejar_tubos(8, 3, 2)
    assert t.tubos_amostras == 24
    assert t.tubos_controles == 2
    assert t.tubos_preparo == 1
    assert t.tubos_totais == 27
    # 27 tubos em estantes de 24 -> 2 estantes
    assert t.racks_necessarios == 2


def test_tubos_com_serie_multiplica_pontos():
    # 4 pontos: amostras 2×3×4 = 24; controles 1×4 = 4; preparo 4 -> 32
    t = calculos.planejar_tubos(2, 3, 1, n_pontos_diluicao=4)
    assert t.tubos_amostras == 24
    assert t.tubos_controles == 4
    assert t.tubos_preparo == 4
    assert t.tubos_totais == 32


def test_tubos_rack_customizado():
    t = calculos.planejar_tubos(10, 1, 0, tubos_por_rack=50)
    assert t.tubos_totais == 11
    assert t.racks_necessarios == 1


def test_tubos_entradas_invalidas():
    with pytest.raises(EntradaInvalida):
        calculos.planejar_tubos(0, 1)
    with pytest.raises(EntradaInvalida):
        calculos.planejar_tubos(1, 0)
    with pytest.raises(EntradaInvalida):
        calculos.planejar_tubos(1, 1, -1)
    with pytest.raises(EntradaInvalida, match="ao menos 1 ponto"):
        calculos.planejar_tubos(1, 1, 0, n_pontos_diluicao=0)
    with pytest.raises(EntradaInvalida):
        calculos.planejar_tubos(1, 1, 0, tubos_por_rack=0)
