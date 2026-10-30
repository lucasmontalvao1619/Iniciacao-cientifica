"""Testes de estatística, com valores conferidos manualmente."""

from __future__ import annotations

import math

import pytest

from planejador.core import estatistica
from planejador.core.exceptions import EntradaInvalida


def test_media():
    assert estatistica.media([2.0, 4.0, 6.0]) == 4.0


def test_desvio_amostral():
    # desvio amostral de [2,4,6] = 2.0
    assert math.isclose(estatistica.desvio_padrao([2.0, 4.0, 6.0]), 2.0)


def test_variancia_amostral():
    assert math.isclose(estatistica.variancia([2.0, 4.0, 6.0]), 4.0)


def test_resumo():
    r = estatistica.resumo([2.0, 4.0, 6.0])
    assert r.n == 3
    assert r.media == 4.0
    assert math.isclose(r.desvio_padrao, 2.0)
    assert r.minimo == 2.0
    assert r.maximo == 6.0


def test_teste_t_grupos_iguais_nao_significativo():
    r = estatistica.teste_t([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert r.significativo is False
    assert math.isclose(r.valor_p, 1.0)


def test_teste_t_grupos_diferentes_significativo():
    r = estatistica.teste_t([1.0, 2.0, 3.0], [100.0, 101.0, 102.0])
    assert r.significativo is True


def test_teste_t_amostra_pequena_erro():
    with pytest.raises(EntradaInvalida):
        estatistica.teste_t([1.0], [2.0, 3.0])


def test_anova_tres_grupos():
    r = estatistica.anova_uma_via(
        [1.0, 2.0, 3.0], [1.1, 2.1, 3.1], [1.2, 2.2, 3.2]
    )
    assert r.n_grupos == 3
    assert r.significativo is False


def test_anova_menos_de_dois_grupos_erro():
    with pytest.raises(EntradaInvalida):
        estatistica.anova_uma_via([1.0, 2.0, 3.0])
