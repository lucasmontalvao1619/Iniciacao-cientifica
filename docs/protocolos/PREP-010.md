# PREP-010 — Meio necessário para placas ou tubos

## Conferência bibliográfica em 08/11/2026

Módulo 5: expediente indica 1ª edição de 2010; copyright/ficha de 2013. Não inferir nova edição nem usar a postagem de 2020 como ano editorial. Conferência e limites em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md).

## Implementação de 08/11/2026

Parâmetros: placas ou tubos (escolha obrigatória), volume por recipiente e unidade (µL/mL/L), quantidade inteira de recipientes já incluindo controles/repetições e excedente percentual escolhido pelo pesquisador (0 = sem reserva). Identificação do meio, formato/capacidade e método de distribuição são textos opcionais; ausências de formato/método ficam pendentes para conferência antes de executar. Um tipo e uma dose por planejamento; grupos diferentes exigem planejamentos separados.

Vbase=N×v; reserva=Vbase×E/100; Vtotal=Vbase×(1+E/100). Não aumentar a dose individual para consumir reserva. Capacidade nominal não é dose recomendada. Não calcula composição/massa de pó, ciclo ou validade. A distribuição e o preparo dependem do método; não são validados automaticamente.

Consulta 2026-11-08T10:51:07.891495-03:00 (America/Maceio). Anvisa módulo 5, 2013, p. 18 (PDF 20): distribuição específica de ágar chocolate com doses distintas para placas/tubos; não generalizar 20 mL/placa ou 6 mL/tubo. BVS MS, Guia Influenza, 2016, p. 48 (PDF 49): dimensionamento e reserva de reações em método específico. Produto N×v e reserva percentual são derivações explícitas do aplicativo, sem margem universal. Fontes completas, horários de obtenção, hashes e páginas em `docs/referencias/fontes/ANVISA-2013-M5-PREP-010.json` e `MS-2016-INFLUENZA-PREP-010.json`. Não equivale a inclusão formal na revisão ou confirmação de última edição.

POP individual e DOCX com balão volumétrico ilustrativo reutilizado, autor Hannes Grobe, CC BY-SA 2.5, URL/hash/data originais preservados. A imagem não impõe equipamento, marca ou capacidade. Dados calculados permanecem distintos de observações; sem validação em bancada.

Verificações: casos independentes (12 placas × 20 mL + 10% = 264 mL; 10 tubos × 6 mL sem reserva = 60 mL), limites/entradas inválidas, edição ao vivo, histórico, JSON, DOCX ilustrado e troca/reinício. Suíte completa: 280 testes aprovados. POP de três páginas e capturas Qt inspecionados.

## Registro anterior preservado

# PREP-010 — Cálculo de meio necessário por número de placas/tubos

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-010.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-010, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: B5 — Microbiology Society.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
