# Casos de uso

Cenários de uso previstos para o sistema.

## Planejamento

| # | Caso de uso | Descrição |
|---|---|---|
| UC01 | Planejar experimento microbiológico | Selecionar protocolo, informar amostras/replicatas/controles e receber o plano operacional |
| UC02 | Planejar preparo de solução | Informar concentração e volume desejados e obter a massa de soluto necessária |
| UC03 | Planejar diluição seriada | Informar concentração inicial, fator e número de pontos e obter as concentrações da série |
| UC04 | Planejar ensaio em microplaca | Informar amostras, replicatas e controles e obter ocupação de poços e número de placas |
| UC05 | Organizar controles experimentais | Reservar poços de controle dentro do planejamento da placa |
| UC06 | Organizar repetições experimentais | Escalonar reagentes e materiais por número de replicatas, com margem de excesso |

## Análise

| # | Caso de uso | Descrição |
|---|---|---|
| UC07 | Analisar dados experimentais | Informar medições por grupo e obter estatística descritiva e teste de hipótese (teste t para dois grupos, ANOVA para três ou mais) |
| UC08 | Registrar resultados da bancada | Criar o experimento executado e lançar as medições por grupo, em uma vez ou em tandas |
| UC09 | Consultar dados tabulados | Recuperar um experimento com as medições em formato longo e o resumo por grupo |
| UC10 | Exportar resultados | Gerar CSV das medições e do resumo estatístico para uso fora do aplicativo |

## Fluxo típico (UC01)

1. O usuário escolhe um protocolo cadastrado.
2. Informa número de amostras, replicatas e controles, a margem de excesso e,
   se houver solução a preparar, as concentrações e o volume.
3. O sistema valida as entradas; se algo estiver inconsistente, devolve a
   mensagem de erro com a dica de correção e aguarda nova entrada.
4. O sistema escalona reagentes e materiais, calcula o preparo da solução, a
   contagem de tubos e a ocupação de microplacas.
5. O sistema devolve o plano operacional consolidado, com o resumo do
   procedimento passo a passo.
6. Após executar o experimento, o usuário registra as medições por grupo.
7. O sistema organiza as medições em tabelas.
8. Se solicitado, aplica a análise estatística e disponibiliza os resultados.

Passos 1 e 6–7 correspondem a `experimento_service`; 2–5 a `gerar_plano`; e
8 a `analisar_experimento` / `exportar_experimento_csv`. Ver
[arquitetura do backend](../arquitetura/backend.md) e `backend/README.md` para
exemplos executáveis.
