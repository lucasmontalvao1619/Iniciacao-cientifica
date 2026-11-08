# PREP-002 — Soluções molares

## Procedência regularizada em 08/11/2026

Cópia integral obtida efetivamente no Arca e idêntica byte a byte à fonte anterior. Consulta 2026-11-08T10:43:13.707165-03:00 (America/Maceio). Volume 1: https://www.arca.fiocruz.br/handle/icict/8658. Datas de obtenção, hashes e comparação em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md). Regras e páginas não mudaram; não equivale a inclusão formal na revisão nem confirmação de edição mais recente.

## Implementação de 08/11/2026

As entradas variáveis são perguntas, sem pressupor massa molar, densidade ou teor de 100%. Identificação de soluto e solvente é opcional para o cálculo numérico. Entradas: soluto e solvente livres, concentração em mol/L, volume final em mL, massa molar em g/mol, teor % m/m e forma de medir o reagente. Para líquido medido por volume, densidade do reagente comercial em g/mL é obrigatória. A massa molar não é calculada pelo nome e deve corresponder à forma química real, incluindo hidratação quando aplicável.

Regras: n = C × V/1000; massa pura = n × MM; massa comercial = massa pura/(T/100). Se medido em volume, volume comercial = massa comercial/d. Solvente q.s.p. ao volume final; nunca usar uma subtração de volumes como medida exata de solvente. Teor acima de 100%, entradas não finitas/não positivas e dose líquida superior ao volume final são rejeitados.

Fonte: EPSJV/IOC/Fiocruz, Conceitos e métodos para a formação de profissionais em laboratórios de saúde, v. 1, 2009. ISBN 978-85-98768-41-0. P. 226 sustenta molaridade e massa molar; p. 229–232, teor, materiais e preparo; p. 249–250, exemplo de correção por teor m/m e densidade (8,29 mL de HCl comercial para o caso descrito no livro). O exemplo valida numericamente a rotina, sem fixar reagente ou solvente no aplicativo.

Fonte e horários: [REGISTRO.md](../../REGISTRO.md) e `docs/referencias/fontes/FIOCRUZ-2009-vol1-PREP-002.json`. A elegibilidade permanece candidata, sem inclusão formal declarada na revisão. A imagem de balão volumétrico é complementar: Hannes Grobe, CC BY-SA 2.5, com URL, licença, horário e hash em `frontend/assets/equipment/balao-volumetrico.json` e no DOCX.

O gráfico é de dimensionamento, não de medições. Não há garantia automática de compatibilidade, solubilidade, estabilidade, concentração de espécies dissociadas ou validação em bancada. Padronização e condições térmicas/armazenamento devem seguir o método do experimento.

## Registro anterior preservado

# PREP-002 — Preparo de soluções molares

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-002.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-002, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: A1 — ANVISA Mód. 5; B2 — UniFatecie.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
