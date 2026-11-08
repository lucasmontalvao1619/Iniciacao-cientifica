# PREP-008 — Preparo de meio a partir de formulação

## Conferência bibliográfica em 08/11/2026

Módulo 5: expediente indica 1ª edição de 2010; copyright/ficha de 2013. Não inferir nova edição nem usar a postagem de 2020 como ano editorial. Conferência e limites em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md).

## Implementação de 08/11/2026

Perguntas específicas: qual formulação, volume nominal de referência e volume nominal alvo. Receita de referência identificada (ágar nutriente, Anvisa 2013 p. 15) é protegida contra alteração; receita livre exige componentes, quantidades, unidades e fonte/versão ou autoria informada pelo pesquisador. Valores de referência da fonte não são respostas presumidas para uma receita livre.

Para referência nominal de 1000 mL, a fonte indica extrato de carne 3 g, peptona 5 g, ágar 15 g e água destilada 1000 mL; pH 6,8 ± 0,2 a 25 °C. Cada ingrediente é multiplicado por Vnominal alvo/Vnominal referência, preservando g/mg/mL/µL. Não somar massa e volume nem reinterpretar água da receita como q.s.p. ao volume final exato.

P. impressa 15 (PDF 17) orienta pesar/hidratar, fundir, distribuir 3–5 mL por tubo e autoclavar. O trecho não especifica ciclo de tempo/temperatura: perguntar ao pesquisador o processo/ciclo definido para o meio e carga, mantendo a ausência como pendência. A referência traz conservação embalada de 4 a 8 °C por até 3 meses; mostrar como condição dessa receita, sem cálculo de data de validade nem generalização a receitas livres. Receitas próprias perguntam também pH, procedimento e conservação/validade, sem herdar parâmetros da referência. Trocar formulação limpa o ciclo anteriormente informado.

Origem: Anvisa, Microbiologia Clínica, módulo 5, 2013, p. 14–15 (PDF 16–17). O campo ISBN está vazio na ficha da cópia e não foi inventado. Original/extração, URL, hash e consultas com data/hora/fuso estão em [REGISTRO.md](../../REGISTRO.md) e ANVISA-2013-M5-PREP-008.json. Manual federal candidato ao recorte, sem inclusão formal na revisão nem confirmação de edição mais recente. Imagem complementar de balança US DEA reutilizada com fonte, licença e data original preservadas.

Saídas: lista de ingredientes escalados, procedimento/origem e pendências de preparo. Resultados permite editar a receita própria e volume, atualizando quantidades e gráfico; um seletor escolhe qual componente visualizar, sem comparar g e mL no mesmo eixo. Receita do pesquisador nunca é apresentada como validada pela Anvisa. Ciclo, controle de qualidade e condições efetivas não são validados automaticamente; cálculo nominal não equivale a execução em bancada.

251 testes passaram na suíte completa, incluindo exemplo independente de 250 mL (0,75/1,25/3,75 g e 250 mL de água), rejeição de alteração da receita identificada, receita livre com unidades preservadas, tipos/limites, recálculo/gráfico, histórico, exportações e mudança de protocolo. Ruff e mypy core/service com imports omitidos aprovados; não é tipagem completa das dependências. Capturas Qt e duas páginas do DOCX ilustrado inspecionadas; página de 880 px sem rolagem horizontal. Campos da tabela dimensionados pela altura real dos widgets para evitar corte.

Pacote Mac PREP-001-a-008 gerado com oito POPs e pasta de registros; assinatura, catálogo e integridade conferidos. Windows ainda não executado.

## Registro anterior preservado

# PREP-008 — Preparo de meio a partir de formulação

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-008.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-008, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: A1 — ANVISA Mód. 5; B2 — UniFatecie; B4 — Microbiologia Aplicada; B5 — Microbiology Society.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
