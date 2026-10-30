# Análise estatística

**Estado: implementado** (backend), exceto a geração de gráficos, que depende da
interface.

Código: `backend/planejador/core/estatistica.py`, `core/tabelas.py` e
`backend/planejador/services/estatistica_service.py`. Usa NumPy, SciPy e Pandas.

## Estatística descritiva

| Função | Devolve |
|---|---|
| `media` | Média aritmética |
| `desvio_padrao` | Desvio padrão (amostral por padrão; `amostral=False` para populacional) |
| `variancia` | Variância (mesma convenção) |
| `erro_padrao` | Erro padrão da média |
| `resumo` | `ResumoDescritivo` com n, média, desvio, variância, erro padrão, mínimo e máximo |

O padrão **amostral** (denominador n−1) é o correto para dados experimentais,
onde as medições são uma amostra e não a população inteira.

## Testes de hipótese

### Teste t — `teste_t(grupo_a, grupo_b, welch=False, alpha=0.05)`

Teste t de Student para **duas amostras independentes**. Com `welch=True`, usa a
correção de Welch, que não assume variâncias iguais entre os grupos.

Devolve `ResultadoTesteT`: estatística t, valor-p, graus de liberdade, o `alpha`
usado e `significativo` (verdadeiro quando p < alpha).

Exige ao menos 2 valores por grupo.

### ANOVA — `anova_uma_via(*grupos, alpha=0.05)`

ANOVA de uma via, para comparar **três ou mais grupos**. Devolve
`ResultadoAnova`: estatística F, valor-p, número de grupos e `significativo`.

Aceita 2 grupos tecnicamente, mas nesse caso a mensagem de erro sugere o teste t.
Exige ao menos 2 valores por grupo.

> A ANOVA indica que **existe** diferença entre os grupos, não **quais** grupos
> diferem. Teste post-hoc (Tukey) não está implementado.

## Escolha automática do teste

`analisar_grupos({"controle": [...], "tratamento": [...]})` calcula o resumo de
cada grupo e escolhe o teste pelo número de grupos:

| Grupos | Teste aplicado |
|---|---|
| 1 | Apenas resumo descritivo |
| 2 | Teste t |
| 3 ou mais | ANOVA de uma via |

Devolve um dicionário com `resumos`, as tabelas estruturadas
(`tabela_medicoes` e `tabela_resumo`) e `teste_t`/`anova` (nulos quando não se
aplicam).

`analisar_experimento(session, experimento_id)` faz o mesmo, mas lendo as
medições salvas no banco, agrupadas pelo campo `grupo` da tabela `medicoes`.

## Organização em tabelas

`core/tabelas.py` transforma o mapa `{grupo: [valores...]}` em `DataFrame`:

| Função | Devolve |
|---|---|
| `tabela_medicoes` | Dados brutos em formato longo: `grupo`, `replicata`, `valor` |
| `tabela_resumo` | Uma linha por grupo: n, média, desvio, variância, erro padrão, CV%, mínimo e máximo |
| `tabela_insumos` | Reagentes/materiais de um plano com quantidade base e total |
| `para_registros` | Converte a tabela em `list[dict]` serializável (NaN/inf viram `None`) |
| `exportar_csv` | Grava a tabela em CSV com `;` e vírgula decimal (Excel em português) |

O **coeficiente de variação** (CV%) é o acréscimo em relação ao `resumo` do
módulo de estatística: é o número que se olha em bancada para julgar a
repetibilidade entre replicatas. Grupos com uma única medição não têm dispersão
definida e recebem `NaN` nessas colunas, em vez de erro.

`exportar_experimento_csv(session, experimento_id, destino)` grava os dois
arquivos (`_medicoes.csv` e `_resumo.csv`) de uma vez.

## Nível de significância

`alpha` é 0,05 por padrão e é parâmetro em todas as funções de teste. O valor
usado volta no resultado, para que o relatório registre sob qual critério a
decisão foi tomada.

## Pendente

Geração de gráficos (RF16). Os dados que a alimentam já estão prontos; falta a
camada de apresentação — ver [frontend](../arquitetura/frontend.md).

## Primeira interface (30/10/2026)

`frontend/analysis.py` apresenta resumos e comparação opcional dos services, além de gráfico de pontos Matplotlib e exportação PNG. A primeira entrega cobre gráfico de pontos por grupo, não todas as visualizações futuras. Entrada em memória, sem gravação automática das medições no banco.
