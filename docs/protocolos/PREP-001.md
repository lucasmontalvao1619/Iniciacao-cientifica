# PREP-001 — Soluções percentuais

## Procedência regularizada em 08/11/2026

Cópia integral obtida efetivamente no Arca e idêntica byte a byte à fonte anterior. Consulta 2026-11-08T10:43:13.707165-03:00 (America/Maceio). Volume 1: https://www.arca.fiocruz.br/handle/icict/8658. Datas de obtenção, hashes e comparação em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md). Regras e páginas não mudaram; não equivale a inclusão formal na revisão nem confirmação de edição mais recente.

## Implementação de 08/11/2026

Cálculo, formulário específico, plano e gráfico de dimensionamento implementados. As entradas variáveis são perguntas; valores numéricos começam sem resposta, incluindo o teor. Não equivale a validação em bancada ou inclusão formal da fonte na revisão. Soluto e solvente são informados pelo pesquisador; não há lista fechada nem verificação automática de compatibilidade/solubilidade.

| Entrada | Base/unidade |
|---|---|
| Concentração C | % m/v, % v/v ou % m/m |
| Quantidade final Q | mL para m/v e v/v; g para m/m |
| Teor/pureza T do rótulo | % m/m em m/v e m/m; % v/v em v/v |
| Soluto e solvente | Identificação livre opcional, até 160 caracteres |

Quantidade pura = Q × C/100; quantidade do reagente comercial = Q × C/T. São rearranjos das definições da p. 227 e da pureza na p. 229. Para m/m, solvente = massa final − massa do reagente comercial. Para m/v e v/v, solvente q.s.p. à quantidade final, sem subtração de volumes como se fossem aditivos. Percentuais m/m e v/v não podem superar o teor do reagente. % m/v pode exceder 100 numericamente; a solubilidade precisa ser verificada para a substância.

Fonte: Molinaro, Caputo e Amendoeira (org.). Conceitos e métodos para a formação de profissionais em laboratórios de saúde, v. 1. EPSJV/IOC/Fiocruz, 2009. ISBN 978-85-98768-41-0.

| Conteúdo | Local | Evidência |
|---|---|---|
| Definições percentuais | p. 227 | PDF FIOCRUZ-2009-vol1.pdf, inspeção visual e texto extraído |
| Pureza e materiais | p. 229–230 | Mesmo PDF |
| Técnica geral e q.s.p. | p. 231–232 | Mesmo PDF; POP reescrito e adaptações identificadas |
| Foto de balança | Wikimedia Commons / US DEA | Domínio público; imagem complementar, fora do corpus; ficha em frontend/assets/equipment/balanca-analitica.json |

URL, edição, horários reais, hash e distinção da situação de elegibilidade estão em [REGISTRO.md](../../REGISTRO.md) e `docs/referencias/fontes/FIOCRUZ-2009-vol1-ficha.json`.

Verificações: casos independentes (9 g em 1 L a 0,9% m/v; correção de pureza; m/m e v/v), entradas inválidas/não finitas, limites de teor, resultados ao vivo, exportação de fontes e DOCX com imagem. Não há demonstração de estabilidade, precisão de equipamento ou execução em bancada.

## Registro anterior preservado

# PREP-001 — Preparo de soluções percentuais (% m/v, v/v e variações aplicáveis)

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-001.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-001, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: A1 — ANVISA Mód. 5; B2 — UniFatecie; B5 — Microbiology Society.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
