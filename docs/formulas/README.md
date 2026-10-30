# Fórmulas

Fórmulas laboratoriais e estatísticas usadas pelo sistema.

> **Fórmulas devem ser documentadas antes da implementação.**

## O que cada fórmula deve registrar

- nome;
- finalidade;
- variáveis de entrada;
- unidade de cada variável;
- expressão matemática;
- condições de uso;
- exemplo conceitual;
- referência;
- módulo relacionado.

## Fórmulas já implementadas

### Laboratoriais

Em `backend/planejador/core/calculos.py`. Detalhe em
[planejamento experimental](../modulos/planejamento-experimental.md).

| Fórmula | Expressão | Condições |
|---|---|---|
| Diluição simples | C₁·V₁ = C₂·V₂ | Todos os valores > 0; C₂ ≤ C₁ |
| Diluição seriada | Cᵢ = C₀ / fatorⁱ | C₀ > 0; fator > 1; n ≥ 1 |
| Massa de soluto | massa = concentração · volume | Ambos > 0; unidades coerentes |
| Escalonamento | total = base · N · (1 + excesso/100) | base > 0; N ≥ 1; excesso ≥ 0 |
| Ocupação de placa | poços = amostras · replicatas · pontos + controles · pontos | Contagens ≥ 1; controles ≥ 0; pontos ≥ 1 |
| Número de placas | ⌈poços / capacidade⌉ | Capacidade ≥ 1 |

**Unidades:** as funções são agnósticas de unidade e exigem apenas coerência
entre as entradas (g/L com L dá g; mg/mL com mL dá mg).

### Estatísticas

Em `backend/planejador/core/estatistica.py`, sobre NumPy e SciPy. Detalhe em
[análise estatística](../modulos/analise-estatistica.md).

| Fórmula | Observação |
|---|---|
| Média | Média aritmética |
| Variância e desvio padrão | Amostral (n−1) por padrão; populacional opcional |
| Erro padrão da média | s / √n |
| Teste t | Duas amostras independentes; correção de Welch opcional |
| ANOVA de uma via | Três ou mais grupos; indica que há diferença, não qual |

O nível de significância (`alpha`) é 0,05 por padrão e é parâmetro em todos os
testes; o valor usado volta no resultado.
