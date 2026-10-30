"""Análise estatística básica de dados experimentais.

Funções puras sobre listas de números, usando NumPy e SciPy. Devolvem
resultados simples (float/dict), sem UI e sem gráficos — a apresentação fica
nas camadas superiores.

Nota sobre ``ddof``: em laboratório trabalha-se quase sempre com amostras, então
o padrão aqui é o desvio/variância **amostral** (``ddof=1``), diferente do
padrão populacional do NumPy.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy import stats

from .exceptions import EntradaInvalida


def _validar_amostra(nome: str, valores: Sequence[float], minimo: int = 1) -> None:
    """Valida que a amostra tem tamanho suficiente e é numérica."""
    if len(valores) < minimo:
        raise EntradaInvalida(
            f"'{nome}' precisa de ao menos {minimo} valor(es) "
            f"(recebido: {len(valores)})."
        )


def media(valores: Sequence[float]) -> float:
    """Média aritmética.

    Example:
        >>> media([2.0, 4.0, 6.0])
        4.0
    """
    _validar_amostra("valores", valores)
    return float(np.mean(valores))


def desvio_padrao(valores: Sequence[float], amostral: bool = True) -> float:
    """Desvio padrão (amostral por padrão, ``ddof=1``).

    Example:
        >>> desvio_padrao([2.0, 4.0, 6.0])
        2.0
    """
    _validar_amostra("valores", valores, minimo=2 if amostral else 1)
    return float(np.std(valores, ddof=1 if amostral else 0))


def variancia(valores: Sequence[float], amostral: bool = True) -> float:
    """Variância (amostral por padrão, ``ddof=1``).

    Example:
        >>> variancia([2.0, 4.0, 6.0])
        4.0
    """
    _validar_amostra("valores", valores, minimo=2 if amostral else 1)
    return float(np.var(valores, ddof=1 if amostral else 0))


def erro_padrao(valores: Sequence[float]) -> float:
    """Erro padrão da média (desvio amostral / raiz(n))."""
    _validar_amostra("valores", valores, minimo=2)
    return float(np.std(valores, ddof=1) / np.sqrt(len(valores)))


@dataclass(frozen=True)
class ResumoDescritivo:
    """Resumo descritivo de uma amostra."""

    n: int
    media: float
    desvio_padrao: float
    variancia: float
    erro_padrao: float
    minimo: float
    maximo: float


def resumo(valores: Sequence[float]) -> ResumoDescritivo:
    """Calcula um resumo descritivo completo da amostra.

    Example:
        >>> r = resumo([2.0, 4.0, 6.0])
        >>> (r.n, r.media, r.desvio_padrao)
        (3, 4.0, 2.0)
    """
    _validar_amostra("valores", valores, minimo=2)
    arr = np.asarray(valores, dtype=float)
    return ResumoDescritivo(
        n=int(arr.size),
        media=float(arr.mean()),
        desvio_padrao=float(arr.std(ddof=1)),
        variancia=float(arr.var(ddof=1)),
        erro_padrao=float(arr.std(ddof=1) / np.sqrt(arr.size)),
        minimo=float(arr.min()),
        maximo=float(arr.max()),
    )


@dataclass(frozen=True)
class ResultadoTesteT:
    """Resultado de um teste t para duas amostras independentes."""

    estatistica_t: float
    valor_p: float
    graus_liberdade: float
    significativo: bool
    alpha: float
    welch: bool


def teste_t(
    grupo_a: Sequence[float],
    grupo_b: Sequence[float],
    *,
    welch: bool = False,
    alpha: float = 0.05,
) -> ResultadoTesteT:
    """Teste t de Student para duas amostras independentes.

    Args:
        grupo_a: Valores do primeiro grupo.
        grupo_b: Valores do segundo grupo.
        welch: Se ``True``, usa o teste de Welch (não assume variâncias iguais).
        alpha: Nível de significância (padrão 0,05).

    Returns:
        :class:`ResultadoTesteT` com estatística, valor-p e decisão.

    Raises:
        EntradaInvalida: Se algum grupo tiver menos de 2 valores.
    """
    _validar_amostra("grupo_a", grupo_a, minimo=2)
    _validar_amostra("grupo_b", grupo_b, minimo=2)
    resultado = stats.ttest_ind(grupo_a, grupo_b, equal_var=not welch)
    t = float(resultado.statistic)
    p = float(resultado.pvalue)
    gl = float(getattr(resultado, "df", len(grupo_a) + len(grupo_b) - 2))
    return ResultadoTesteT(
        estatistica_t=t,
        valor_p=p,
        graus_liberdade=gl,
        significativo=p < alpha,
        alpha=alpha,
        welch=welch,
    )


@dataclass(frozen=True)
class ResultadoAnova:
    """Resultado de uma ANOVA de uma via."""

    estatistica_f: float
    valor_p: float
    n_grupos: int
    significativo: bool
    alpha: float


def anova_uma_via(
    *grupos: Sequence[float], alpha: float = 0.05
) -> ResultadoAnova:
    """ANOVA de uma via para comparar três ou mais grupos.

    Args:
        *grupos: Duas ou mais amostras (recomenda-se três ou mais).
        alpha: Nível de significância (padrão 0,05).

    Returns:
        :class:`ResultadoAnova` com estatística F, valor-p e decisão.

    Raises:
        EntradaInvalida: Se houver menos de 2 grupos ou algum grupo com < 2
            valores.
    """
    if len(grupos) < 2:
        raise EntradaInvalida(
            "A ANOVA exige ao menos 2 grupos (idealmente 3 ou mais).",
            dica="Para exatamente 2 grupos, considere usar o teste t.",
        )
    for i, g in enumerate(grupos):
        _validar_amostra(f"grupo_{i + 1}", g, minimo=2)
    f, p = stats.f_oneway(*grupos)
    return ResultadoAnova(
        estatistica_f=float(f),
        valor_p=float(p),
        n_grupos=len(grupos),
        significativo=float(p) < alpha,
        alpha=alpha,
    )
