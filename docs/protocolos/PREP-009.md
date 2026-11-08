# PREP-009 — Meio comercial desidratado

## Conferência bibliográfica em 08/11/2026

Módulo 5: expediente indica 1ª edição de 2010; copyright/ficha de 2013. Não inferir nova edição nem usar a postagem de 2020 como ano editorial. Conferência e limites em [regularização das fontes](../referencias/REGULARIZACAO_FONTES.md).

## Implementação de 08/11/2026

Perguntas específicas: massa recomendada em g, volume de referência em mL, volume desejado em mL e se a instrução define volume de água ou volume final. Números começam sem resposta e a convenção de volume exige escolha explícita. Produto é identificação opcional; rótulo/documento e versão que fundamentam a proporção devem ser informados.

Massa alvo=massa de referência×V alvo/V referência, usando o núcleo de escala já existente. Se a instrução define água, escalar esse volume sem chamá-lo de volume final exato. Somente na convenção final indicar q.s.p. Não adotar proporção por nome comercial nem concentração universal. Campos de preparo perguntam procedimento, pH, ciclo, suplementos (inclusive declaração de nenhum) e conservação/validade; ausências ficam pendentes e não impedem o dimensionamento numérico válido.

Documento e consulta particular do fabricante são declarados pelo pesquisador, separados da fonte técnica do aplicativo; não afirmar leitura automática de um rótulo não consultado. Consulta declarada pode permanecer desconhecida e não gera data fictícia. Sem validar automaticamente condições ou calcular prazo de validade.

Fonte técnica: Anvisa, Microbiologia Clínica, módulo 5, 2013, p. 7–8 e 11 (PDF 9–10 e 13). Hidratação/pesagem e observância da instrução do fabricante. A introdução menciona ciclo normalmente 121 °C/15 min, mas prioriza rótulo/manual; esse ciclo não vira regra universal. Fonte, edição, hash, horários reais e imagem complementar em [REGISTRO.md](../../REGISTRO.md) e ANVISA-2013-M5-PREP-009.json. Manual federal candidato ao recorte, sem inclusão formal na revisão ou confirmação de edição mais recente.

Plano e Resultados mostram massa, convenção de volume, referência declarada e pendências. Edição recalcula massa/gráfico e o mesmo registro do histórico. Exportação JSON preserva os dados declarados e as fontes técnicas. POP do protocolo individual, ilustrado com balança creditada.

265 testes passaram na suíte completa, incluindo casos independentes (26 g/1000 mL para 250 mL resulta 6,5 g; caso sintético para verificar matemática, não prescrição de produto), água/final, entradas inválidas, recálculo, histórico, exportações e troca de protocolo. Ruff e mypy do service com imports omitidos aprovados; sem tipagem completa das dependências. Capturas Qt e duas páginas do DOCX inspecionadas; página de 880 px sem rolagem horizontal, rótulos sem corte. Não há validação de instrução comercial, ciclo ou uso em bancada.

Pacote Mac PREP-001-a-009 gerado com nove POPs e pasta de registros; assinatura, catálogo e integridade conferidos. Windows ainda não executado.

## Registro anterior preservado

# PREP-009 — Preparo de meio comercial desidratado

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-009.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-009, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: A1 — ANVISA Mód. 5; B5 — Microbiology Society.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
