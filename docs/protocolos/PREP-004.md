# PREP-004 — Diluição de solução-estoque

## Procedência regularizada em 08/11/2026

Cópia integral obtida efetivamente no Arca e idêntica byte a byte à fonte anterior. Consulta 2026-11-08T10:43:13.707165-03:00 (America/Maceio). Volume 1: https://www.arca.fiocruz.br/handle/icict/8658. Datas de obtenção, hashes e comparação em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md). Regras e páginas não mudaram; não equivale a inclusão formal na revisão nem confirmação de edição mais recente.

## Implementação de 08/11/2026

Perguntar concentração do estoque C1, concentração desejada C2, unidade comum de concentração e volume final V2 em mL. Identificação do estoque e do diluente são livres e opcionais no cálculo. Não presumir valores físicos.

Fonte: Fiocruz 2009, p. 230–232, principalmente equação de diluição na p. 232. Edição, URL, consulta com fuso e hash em [REGISTRO.md](../../REGISTRO.md) e FIOCRUZ-2009-vol1-PREP-004.json. Fonte candidata ao recorte federal em português desde 2000, sem inclusão formal na revisão.

V1 = V2 × C2/C1. Concentrações devem usar a mesma base por volume. Unidades disponíveis: mg/mL, µg/mL, g/L, mol/L, mmol/L, U/mL, % m/v e % v/v. Não converter % m/m por esta fórmula volumétrica. O fator C1/C2 é adimensional. C2 maior que C1 não é diluição; igualdade significa ausência de diluição. Todos os valores devem ser positivos e finitos; rejeitar resultados fora da faixa numérica.

Transferir alíquota calculada e completar com diluente q.s.p. ao volume final, conforme método, compatibilidade e condições térmicas. Diferença V2−V1 é nominal e não deve ser apresentada como volume exato a adicionar. Instrumento e tolerância devem ser compatíveis com o volume de alíquota. Não substitui checagem de solubilidade, estabilidade, atividade ou padronização exigida pelo método. Gráfico é dimensionamento, sem simular medições.

Verificação: 181 testes passaram na suíte completa, incluindo conservação de soluto, exemplo 1 mol/L para 0,1 mol/L em 10 mL (alíquota de 1 mL), fator 1, unidades incompatíveis, entradas inválidas, gráfico ao vivo, histórico e exportações. Capturas Qt de parâmetros e resultados conferidas e janela de 880 px sem rolagem horizontal. DOCX ilustrado renderizado e conferido em duas páginas. Não há validação em bancada.

Pacote Mac PREP-001-a-004 gerado com os quatro POPs e pasta de registros; assinatura, catálogo e integridade do ZIP conferidos. Windows ainda não executado.

## Registro anterior preservado

# PREP-004 — Diluição de solução-estoque

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-004.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-004, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: C2 — CLSI M07; C4 — CLSI M27; C5 — CLSI M38; B5 — Microbiology Society.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
