# PREP-005 — Diluição seriada / sucessiva

## Procedência regularizada em 08/11/2026

Cópia integral obtida efetivamente no Arca e idêntica byte a byte à fonte anterior. Consulta 2026-11-08T10:43:13.707165-03:00 (America/Maceio). Volume 1: https://www.arca.fiocruz.br/handle/icict/8658. Volume 4: https://www.arca.fiocruz.br/handle/icict/8661; divergência de ano/ISBN preservada. Datas de obtenção, hashes e comparação em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md). Regras e páginas não mudaram; não equivale a inclusão formal na revisão nem confirmação de edição mais recente.

## Implementação de 08/11/2026

Cálculo, perguntas próprias, tabela de concentrações/volumes e gráfico editável implementados. Perguntas: concentração inicial C0 e unidade por volume, fator F > 1, número de diluições N sem contar estoque, volume V preparado em cada etapa antes de transferir ao próximo e opção de retirar uma alíquota do último para igualar os volumes. N de 1 a 100 na interface; valores físicos começam sem resposta. Identificação de estoque/diluente é livre e opcional.

Etapa 1 é a primeira diluição: Ck = C0/F^k. Alíquota a = V/F; diluente nominal V−a por etapa. Intermediários ficam com V−a após transferir ao próximo; último mantém V ou V−a conforme a escolha do pesquisador. O gráfico identifica estoque como etapa 0 e usa escala logarítmica. Não interpreta contagem de colônias, preparo de amostra sólida nem atividade após decaimento.

Fonte matemática: Fiocruz v. 1, 2009, p. 232. Técnica sucessiva: Fiocruz v. 4, copyright 2010, p. 441–442. A ficha catalográfica deste PDF reproduz dados do volume 1; ISBN do volume 4 não foi confirmado. Registro institucional da coleção indica 2012, sem resolver a edição desta cópia. Discrepâncias preservadas nas fichas, sem afirmar edição mais recente ou inclusão formal na revisão. Origem, páginas, datas/horários com fuso, hashes e tentativas estão em [REGISTRO.md](../../REGISTRO.md).

As equações de volume restante e a decisão sobre a retirada final são derivações/convenções explícitas da implementação. Volumes são nominais: conferir compatibilidade, aferição, condições do método e tolerância do instrumento. Não importar condições de cultivo/salina do exemplo micológico para todo laboratório. Sem validação em bancada.

Verificações: 202 testes passaram na suíte completa, incluindo balanços de volume e soluto, fatores 2/10, etapa única e limite de 100, igualdade de volumes opcional, entradas inválidas e perda de faixa numérica, edição com tabela/gráfico, histórico, JSON e DOCX ilustrado. Ruff aprovado; mypy dos módulos alterados com imports omitidos, sem afirmar tipagem completa das dependências. POP renderizado e conferido em três páginas; capturas Qt inspecionadas, janela de 880 px sem rolagem horizontal da página. Imagem complementar de balão volumétrico reutilizada com autor, licença, URL, hash e data original.

Pacote Mac PREP-001-a-005 gerado com cinco POPs e pasta de registros; assinatura, catálogo e integridade verificados. Windows ainda não executado.

## Registro anterior preservado

# PREP-005 — Diluição seriada / sucessiva

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-005.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-005, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: B1 — Vermelho et al.; B4 — Microbiologia Aplicada; B5 — Microbiology Society.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
