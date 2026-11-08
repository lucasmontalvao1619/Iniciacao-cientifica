# PREP-003 — Solução-estoque

## Procedência regularizada em 08/11/2026

Cópia integral obtida efetivamente no Arca e idêntica byte a byte à fonte anterior. Consulta 2026-11-08T10:43:13.707165-03:00 (America/Maceio). Volume 1: https://www.arca.fiocruz.br/handle/icict/8658. Datas de obtenção, hashes e comparação em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md). Regras e páginas não mudaram; não equivale a inclusão formal na revisão nem confirmação de edição mais recente.

## Implementação em desenvolvimento de 08/11/2026

Cálculo, perguntas condicionais, plano, gráfico de dimensionamento e exportações implementados no código e cobertos por testes. DOCX ilustrado renderizado e conferido em três páginas. Pacote Mac PREP-001-a-003 gerado com assinatura e integridade verificadas; a sessão aberta do Desktop foi preservada. Windows permanece preparado para teste posterior.

Perguntas ao pesquisador: unidade (mg/mL, µg/mL, g/L, mol/L ou U/mL), concentração desejada, volume final, medição por massa ou volume e correção por pureza, potência ou atividade certificada. Massa molar é necessária somente em mol/L; densidade, somente para medir o reagente comercial por volume. Valores físicos começam sem resposta.

Para concentração massiva e pureza, calcular massa comercial = massa pura/(teor/100), com conversão explícita de unidades. Para potência em µg/mg, massa em mg = V em mL × C em µg/mL / potência. Para U/mL e U/mg, usar o pareamento direto. Se o certificado estiver em U/mg e o alvo em massa/volume, perguntar a equivalência específica em U/µg: potência em µg/mg = atividade/equivalência. Nunca assumir um fator universal.

Identificação de reagente/solvente é livre e opcional no cálculo. Solvente de dissolução e diluente final podem ser distintos; diluente vazio usa o mesmo solvente. Completar q.s.p. ao volume final, sem subtrair volumes como se fossem aditivos.

Identificação do estoque, lote, responsável, data de preparo, validade, conservação e fonte de estabilidade são perguntas opcionais durante o planejamento. Ausências ficam pendentes; erros de datas são apontados sem impedir o dimensionamento numérico. Não inventar prazo ou temperatura de conservação. O método e a compatibilidade devem ser conferidos antes de executar o preparo.

Fontes: Fiocruz 2009, p. 226–234 (concentrações, preparo e identificação); Anvisa 2020, módulo 10, p. 110–111 (massa/potência e solvente/diluente). Edição, URL, hash, datas e horários reais em [REGISTRO.md](../../REGISTRO.md) e nas fichas em `docs/referencias/fontes/`. Condições de antimicrobianos não são generalizadas a outras substâncias. Fontes candidatas ao recorte, sem inclusão formal declarada nem validação de bancada.

## Registro anterior preservado

# PREP-003 — Preparo de solução-estoque

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-003.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-003, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: C2 — CLSI M07; C4 — CLSI M27; C5 — CLSI M38.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
