# REGISTRO — origem dos protocolos

Registro de rastreabilidade para apoiar a revisão sistemática. Criado em 30/10/2026 a pedido de Lucas. Cada nova consulta deve acrescentar uma entrada; preservar o histórico e nunca substituir datas antigas por uma data estimada.

## Como interpretar as entradas atuais

Os dez itens abaixo foram localizados **no catálogo técnico F03**, não diretamente nas obras originais. A data e o horário são os da consulta/importação do catálogo local, já registrados no projeto. **Não comprovam busca executada nos portais, leitura das fontes primárias ou inclusão no corpus da revisão.**

**F03:** Catálogo e priorização de protocolos microbiológicos, v1.0, agosto/2026. [Documento no Drive](https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit). Evidência estruturada: [catálogo da interface](frontend/protocolos.json). Localização: tabela de preparações, pelo identificador de cada item. Páginas das fontes primárias: pendentes de conferência.

## Entradas já documentadas

| Protocolo | Onde foi encontrado | Dia da consulta ao catálogo | Horário | Fuso | Fontes indicadas pelo catálogo, ainda não consultadas nesta inclusão |
|---|---|---|---|---|---|
| [PREP-001 — Preparo de soluções percentuais (% m/v, v/v e variações aplicáveis)](docs/protocolos/PREP-001.md) | F03, tabela de preparações, PREP-001 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | A1 — ANVISA Mód. 5; B2 — UniFatecie; B5 — Microbiology Society |
| [PREP-002 — Preparo de soluções molares](docs/protocolos/PREP-002.md) | F03, tabela de preparações, PREP-002 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | A1 — ANVISA Mód. 5; B2 — UniFatecie |
| [PREP-003 — Preparo de solução-estoque](docs/protocolos/PREP-003.md) | F03, tabela de preparações, PREP-003 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | C2 — CLSI M07; C4 — CLSI M27; C5 — CLSI M38 |
| [PREP-004 — Diluição de solução-estoque](docs/protocolos/PREP-004.md) | F03, tabela de preparações, PREP-004 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | C2 — CLSI M07; C4 — CLSI M27; C5 — CLSI M38; B5 — Microbiology Society |
| [PREP-005 — Diluição seriada / sucessiva](docs/protocolos/PREP-005.md) | F03, tabela de preparações, PREP-005 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | B1 — Vermelho et al.; B4 — Microbiologia Aplicada; B5 — Microbiology Society |
| [PREP-006 — Cálculo de fator de diluição e concentração final](docs/protocolos/PREP-006.md) | F03, tabela de preparações, PREP-006 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | B4 — Microbiologia Aplicada; B5 — Microbiology Society |
| [PREP-007 — Cálculo de volume total e percentual excedente](docs/protocolos/PREP-007.md) | F03, tabela de preparações, PREP-007 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | B5 — Microbiology Society |
| [PREP-008 — Preparo de meio a partir de formulação](docs/protocolos/PREP-008.md) | F03, tabela de preparações, PREP-008 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | A1 — ANVISA Mód. 5; B2 — UniFatecie; B4 — Microbiologia Aplicada; B5 — Microbiology Society |
| [PREP-009 — Preparo de meio comercial desidratado](docs/protocolos/PREP-009.md) | F03, tabela de preparações, PREP-009 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | A1 — ANVISA Mód. 5; B5 — Microbiology Society |
| [PREP-010 — Cálculo de meio necessário por número de placas/tubos](docs/protocolos/PREP-010.md) | F03, tabela de preparações, PREP-010 | 2026-10-30 | 04:56:36 | America/Maceio (-03:00) | B5 — Microbiology Society |

Os registros `incluido_em` no JSON coincidem com a consulta ao catálogo acima; isso não deve ser presumido em inclusões futuras. **Data/hora de obtenção dos procedimentos, materiais, parâmetros e fórmulas nas fontes primárias: não registrada.** As dez fichas identificam essas lacunas; não atribuir regras às obras apenas citadas por F03.

Os dois exemplos antigos — solução salina 0,9% e crescimento em microplaca — vêm de `backend/planejador/database/seed.py`. Sua origem científica e o dia/horário de obtenção não estão registrados. São demonstrativos e não são incluídos como obras/protocolos da revisão por esta tabela.

## Prioridade das buscas

Priorizar **Arca, BVS MS, Anvisa, Manuais SDA, Alice, Infoteca-e, eduCAPES e Oasisbr**, conforme a metodologia vigente. Conferir critérios de elegibilidade, documento completo, edição, páginas e idioma. Estar no portal não garante elegibilidade; fonte técnica complementar deve ser identificada e justificada.

## Acrescentar a cada nova consulta ou extração

Registrar o instante real com fuso, preferencialmente ISO 8601. Distinguir descoberta, consulta ao documento, extração e inclusão no aplicativo. Não preencher “agora” como data de uma consulta antiga desconhecida.

| ID do protocolo | Evento | Documento, instituição e edição | Portal e URL direta | Dia | Horário e fuso | Páginas/trechos, conteúdo obtido e evidência local | Situação na revisão |
|---|---|---|---|---|---|---|---|

Para cada procedimento, material/reagente, unidade, fórmula ou limite, indicar a fonte e a página correspondente na ficha. Guardar a cópia consultada quando disponível. Se houver várias fontes, registrar uma consulta por fonte e explicitar qual sustenta cada parte. Se o dado não existir, escrever **não registrado** ou **pendente**, sem inventar.

Este registro apoia a revisão; estratégias de busca, contagens, triagem e motivos de exclusão continuam exigindo seus próprios registros de execução. Regras completas: [documentação dos protocolos](docs/protocolos/README.md).
