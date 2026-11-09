import pytest

from planejador.core import estatistica
from planejador.core.exceptions import EntradaInvalida


@pytest.mark.parametrize(
    "values", [[1, float("nan")], [1, float("inf")], [1, True], [1, "2"]]
)
def test_nonfinite_or_nonnumeric_rejected(values):
    with pytest.raises(EntradaInvalida):
        estatistica.resumo(values)


@pytest.mark.parametrize("alpha", [0, 1, -0.1, float("nan"), True])
def test_alpha_domain(alpha):
    with pytest.raises(EntradaInvalida):
        estatistica.teste_t([1, 2, 3], [2, 4, 6], alpha=alpha)
    with pytest.raises(EntradaInvalida):
        estatistica.anova_uma_via([1, 2, 3], [2, 4, 6], [3, 4, 7], alpha=alpha)
