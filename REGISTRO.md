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

## Consulta PREP-001 em 2026-11-08T05:02:54.967221-03:00

- Fonte: Conceitos e métodos para a formação de profissionais em laboratórios de saúde volume 1. EPSJV/IOC/Fiocruz, 2009. ISBN 978-85-98768-41-0.
- URL: https://www.epsjv.fiocruz.br/sites/default/files/l140.pdf
- Obtenção: 2026-11-08T05:00:24.136688-03:00; consulta/extração: 2026-11-08T05:02:54.967221-03:00 (America/Maceio).
- Páginas 227–232: definições de % m/v, m/m e v/v, pureza, vidraria e técnica de preparo. Leitura do PDF integral disponível localmente; inspeção visual da p. 227.
- Evidência: docs/referencias/fontes/FIOCRUZ-2009-vol1.pdf, SHA-256 35206a3d5079758e26eaa6fcb343ead6aa7dac4674cbc6ec71d8015437e46b1c.
- Elegibilidade: candidato federal em português desde 2000; acesso direto EPSJV, sem registro Arca localizado até aqui. Não contabilizado como obra incluída em revisão.
- Adaptações para o software: rearranjo algébrico das definições percentuais; pureza deve usar a mesma base da concentração. Volume de solvente é q.s.p., sem presumir volumes aditivos em % v/v.

### Imagem complementar para PREP-001 — 2026-11-08T05:03:37.389821-03:00

https://commons.wikimedia.org/wiki/File:Analytical_balance_mettler_ae-260.jpg. Autor: US DEA; Domínio público — obra do governo federal dos Estados Unidos, conforme ficha do Wikimedia Commons. Evidência: frontend/assets/equipment/balanca-analitica.jpg e respectivo JSON; SHA-256 2ce25d728801e09c66482589d7988ed9bf94d3730c43adab6b34c6854e1f083f. Imagem obtida sem alteração, não é fonte científica do protocolo e não integra o corpus da revisão.

## Consulta PREP-002 — 2026-11-08T05:22:45.047138-03:00

Fiocruz, Conceitos e métodos, volume 1, EPSJV/IOC, 2009, ISBN 978-85-98768-41-0. URL: https://www.epsjv.fiocruz.br/sites/default/files/l140.pdf. PDF preservado e obtido em 2026-11-08T05:00:24.136688-03:00; consulta/extração para este protocolo: 2026-11-08T05:22:45.047138-03:00, America/Maceio. P. 226: molaridade e massa molar; p. 229–232: pureza e técnica; p. 249–250: massa, teor m/m e densidade de reagente líquido. Evidência: docs/referencias/fontes/FIOCRUZ-2009-vol1-PREP-002.json; SHA-256 do PDF 35206a3d5079758e26eaa6fcb343ead6aa7dac4674cbc6ec71d8015437e46b1c. Não implica inclusão formal na revisão. A pesquisa no Infoteca identificou Circular Técnica 42 como folheto de 2000, mas seu uso como livro/manual não foi presumido.

Imagem de balão volumétrico: Hannes Grobe, https://commons.wikimedia.org/wiki/File:Volumetric_flask_hg.jpg, CC BY-SA 2.5 — https://creativecommons.org/licenses/by-sa/2.5/. Obtida em 2026-11-08T05:22:45.047138-03:00; SHA-256 6c57ade5d99e14e4cfb2f20470631732759694caf2073a723fa9a4565b372122. Evidência e atribuição em frontend/assets/equipment/balao-volumetrico.json. Imagem complementar separada das fontes científicas.

## Consulta PREP-003 — 2026-11-08T05:37:29.953373-03:00

- ANVISA, Microbiologia Clínica, módulo 10, 1ª ed., 2020. ISBN 978-65-89701-01-9. Portal Anvisa, URL https://www.gov.br/anvisa/pt-br/centraisdeconteudo/publicacoes/servicosdesaude/publicacoes/modulo-10_manual-de-microbiologia.pdf/@@download/file. Obtenção: 2026-11-08T05:34:55.508307-03:00; extração: 2026-11-08T05:37:29.953373-03:00, America/Maceio. P. 110–111: fórmula massa/volume/potência, exemplo 12,88 mg para 1 mL de estoque de 10.000 µg/mL a potência de 776 µg/mg; distinção entre solvente e diluente. SHA-256 0c131e9699c2652525df9af8ed3aadf2574c393ffd6f103872204be4b4d36e5e. Evidência: ANVISA-Modulo-10.pdf e ANVISA-2020-M10-PREP-003.json. Manual federal com elegibilidade candidata, não inclusão formal.
- A conversão de U em µg exibida para o exemplo não é uma constante universal. Implementar unidades pareadas U/mL e U/mg por análise dimensional, sem copiar um fator fixo para outras substâncias. Essa é uma adaptação explícita, sem alegar validação dessa equivalência para qualquer fármaco.
- FIOCRUZ, Conceitos e métodos, v. 1, 2009. URL https://www.epsjv.fiocruz.br/sites/default/files/l140.pdf; PDF obtido 2026-11-08T05:00:24.136688-03:00; nova consulta 2026-11-08T05:37:29.953373-03:00. P. 226–232: concentração/preparo; p. 233–234: rótulo e conservação conforme substância. Evidência: FIOCRUZ-2009-vol1-PREP-003.json e PDF preservado.
- Imagem ilustrativa reutilizada de balança: US DEA, domínio público; obtenção original preservada em frontend/assets/equipment/balanca-analitica.json. Não é fonte científica nem inclusão na revisão.

### Adaptação dimensional e perguntas em PREP-003

Quando o certificado usa U/mg e o alvo usa massa/volume, solicitar a equivalência específica em U/µg ao pesquisador; não assumir o fator de um composto. O exemplo impresso de 12,88 mg corresponde à fórmula 10000/776 = 12,8865979… mg; o cálculo conserva a fórmula sem reproduzir o truncamento. Esta nota explicita a implementação a partir da consulta acima, sem atribuir nova obtenção à fonte.

## Consulta PREP-004 — 2026-11-08T06:06:38.793144-03:00

Fiocruz, EPSJV/IOC, Conceitos e métodos, v. 1, 2009. ISBN 978-85-98768-41-0. URL https://www.epsjv.fiocruz.br/sites/default/files/l140.pdf. PDF obtido em 2026-11-08T05:00:24.136688-03:00; nova consulta local em 2026-11-08T06:06:38.793144-03:00 (America/Maceio). P. 232: conservação do soluto e C1 V1 = C2 V2; p. 230–231: materiais, transferência e completar o volume final. PDF e extração preservados; SHA-256 35206a3d5079758e26eaa6fcb343ead6aa7dac4674cbc6ec71d8015437e46b1c. A tentativa de acesso web nesta consulta retornou 502; regras conferidas na cópia integral local, não em novo download. Elegibilidade candidata, sem inclusão formal nem comprovação de edição mais recente.

Adaptação explícita: concentrações na mesma unidade por volume; % m/m excluído desta rotina volumétrica. V1 = V2 × C2/C1; fator = C1/C2; V2−V1 é apenas diferença nominal, não dose exata de diluente. Completar q.s.p. ao volume final. C2>C1 é incompatível; C2=C1 não requer diluição. Foto de balão reutilizada, Hannes Grobe, CC BY-SA 2.5, obtenção original 2026-11-08T05:22:45.047138-03:00; crédito, URL e hash no catálogo/POP. Não representa uma nova obtenção da imagem.

## Consulta PREP-005 — 2026-11-08T06:14:11.240645-03:00

Fiocruz v. 4, copyright 2010, p. 441–442: transferências seriadas, homogeneização e pipeta por transferência. URL https://www.ioc.fiocruz.br/sites/default/files/ConceitosMetodos_volume4.pdf. PDF obtido e consulta registrada em 2026-11-08T06:14:11.240645-03:00 (America/Maceio), SHA-256 7d86374dd3be6d0e5196874cd510423f35fa96deb33e9fce2c08f4f39e6d0f8c. Arquivos FIOCRUZ-volume4.pdf/.txt e FIOCRUZ-2010-vol4-PREP-005.json preservados. Capa/folha de rosto identificam v. 4; a ficha catalográfica reproduz v. 1/2009 e seu ISBN: não atribuir esse ISBN ao v. 4. Livro candidato, sem inclusão formal na revisão. O download com urllib falhou por certificado local; curl com verificação TLS padrão obteve o PDF, sem desativar verificação.

Fiocruz v. 1, 2009, p. 232, cópia obtida em 2026-11-08T05:00:24.136688-03:00, nova consulta 2026-11-08T06:14:11.240645-03:00. Equação C1 V1 = C2 V2 e sequência gráfica. Hash 35206a3d5079758e26eaa6fcb343ead6aa7dac4674cbc6ec71d8015437e46b1c. Derivações explícitas: Ck=C0/F^k; alíquota=V/F; diferença nominal=V−alíquota; intermediários perdem alíquota para o seguinte. A opção de retirar alíquota do último para igualar volumes é uma decisão perguntada ao pesquisador, não condição universal da fonte. Volumes são nominais e pressupõem mistura compatível; não inferir culturas/condições de incubação do exemplo.

Imagem de balão reutilizada com crédito Hannes Grobe, CC BY-SA 2.5, URL/hash e data original de obtenção preservados no catálogo e DOCX. Não é nova obtenção de imagem nem fonte científica.

Consulta bibliográfica complementar 2026-11-08T06:19:04.124562-03:00: https://www.rets.epsjv.fiocruz.br/es/node/1849. Registro institucional da coleção indica ano 2012 e postagem 23/06/2016; isso não resolve a data/edição desta cópia do volume 4 (copyright 2010; ficha reproduz volume 1). Link Parte IV retornou 502 na ferramenta web. Preservada a discrepância, sem afirmar edição mais recente nem inventar ISBN.

## Consulta PREP-006 — 2026-11-08T06:27:07.978322-03:00

Fiocruz, EPSJV/IOC, Conceitos e métodos, v. 1, 2009, ISBN 978-85-98768-41-0. https://www.epsjv.fiocruz.br/sites/default/files/l140.pdf. PDF obtido em 2026-11-08T05:00:24.136688-03:00, consulta local em 2026-11-08T06:27:07.978322-03:00 (America/Maceio). P. 232: conservação do soluto e equação de diluição; p. 230–231: materiais, transferência e aferição. Cópia integral e extração preservadas, SHA-256 35206a3d5079758e26eaa6fcb343ead6aa7dac4674cbc6ec71d8015437e46b1c. Não houve novo download; rearranjos explícitos F=V2/V1 e C2=C1×V1/V2, usando a mesma base de concentração por volume e volumes em mL. Diferença V2−V1 somente nominal; não substituir completar q.s.p. por soma de volumes presumidamente aditivos. Livro candidato, sem inclusão formal na revisão ou comprovação de edição mais recente.

Imagem complementar de balão reutilizada com autoria Hannes Grobe, CC BY-SA 2.5, URL/hash e obtenção original 2026-11-08T05:22:45.047138-03:00 preservados. Não representa nova obtenção nem fonte científica.

## Consulta PREP-007 — 2026-11-08T09:51:59.642721-03:00

Ministério da Saúde, Guia para a Rede Laboratorial de Vigilância de Influenza no Brasil, 1ª ed. eletrônica, 2016. ISBN 978-85-334-2402-9. URL https://bvsms.saude.gov.br/bvs/publicacoes/guia_laboratorial_influenza_vigilancia_influenza_brasil.pdf, BVS MS. PDF obtido 2026-11-08T06:32:40.915588-03:00; consulta 2026-11-08T09:51:59.642721-03:00, America/Maceio. P. impressa 48 (PDF 49): multiplicar volume por número de reações e reserva específica por perdas. SHA-256 0338bdad575528844378dc3fbc94533677e9a18458dffe281c3f791e0bcb0fb1; original/extração e MS-2016-INFLUENZA-PREP-007.json preservados. Guia técnico federal candidato, sem inclusão formal nem comprovação de edição mais recente.

Adaptação explícita para calculadora geral: Vbase=v×N; excedente Vbase×E/100; total Vbase×(1+E/100). Percentual livre do pesquisador, inclusive zero; não aplicar universalmente a regra específica +1/+2 reações do guia. N já inclui todas as unidades/controles/repetições. Isso dimensiona um volume de composição definida pelo método, sem inventar uma formulação. Não confundir acréscimo percentual sobre base com perda percentual do total preparado.

Imagem nova: Micropipette Dr pipette.png, Emicropipette, Wikimedia Commons. Fonte https://commons.wikimedia.org/wiki/File:Micropipette_Dr_pipette.png; licença CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/. Obtida 2026-11-08T09:49:17.088101-03:00, SHA-256 381ca2c867862adc0dbc960aef7f2a5485c3cd791a52d34b4770b273f90b3761; original e ficha preservados em frontend/assets/equipment/. Imagem inspecionada, apenas dimensionada; sem recomendação obrigatória de marca ou equipamento. Complementar e fora do corpus científico.

## Consulta PREP-008 — 2026-11-08T10:01:15.935751-03:00

Anvisa, Microbiologia Clínica, módulo 5, 2013, p. 14–15. URL https://www.gov.br/anvisa/pt-br/centraisdeconteudo/publicacoes/servicosdesaude/publicacoes/modulo-5-tecnologias-em-servicos-de-saude-descricao-dos-meios-de-cultura-empregados-nos-exames-microbiologicos/@@download/file, portal Anvisa. Obtenção 2026-11-08T09:57:05.171864-03:00, consulta 2026-11-08T10:01:15.935751-03:00 (America/Maceio), SHA-256 99821377c62d1d23f8598551e6c0d560c17869735fe482529cb34ab851363cee. Original/extração e ANVISA-2013-M5-PREP-008.json preservados. ISBN não preenchido na ficha do PDF; não inventar. Manual candidato ao recorte, sem inclusão formal ou comprovação de edição mais recente.

P. 15: ingredientes do ágar nutriente e água de referência 1000 mL; pH 6,8 ± 0,2 a 25 °C; pesar/hidratar, fundir, distribuir e autoclavar. Não há ciclo de tempo/temperatura no trecho. Derivação explícita: multiplicar cada ingrediente pelo volume nominal alvo/volume nominal de referência, preservando unidades. Não reinterpretar água 1000 mL como q.s.p. ao volume final sem indicação. Ciclo e demais condições variáveis são perguntas ao pesquisador. Receita livre/modificada tem autoria/fonte informada pelo pesquisador e não é apresentada como validada pela Anvisa. Imagem de balança US DEA reutilizada, com fonte/licença/hash e obtenção original preservados.

Consulta visual complementar PREP-008 2026-11-08T10:10:50.353545-03:00: p. impressa 15 = PDF 17; p. 14 = PDF 16. Além da fórmula e preparo, a fonte indica conservação embalada de 4 a 8 °C por até 3 meses. Exibir como condição da receita de referência, sem generalizar às receitas livres nem calcular validade automaticamente. Ciclo de tempo/temperatura da autoclave continua ausente no trecho e deve ser perguntado.

## Consulta PREP-009 — 2026-11-08T10:24:55.493522-03:00

Anvisa, Microbiologia Clínica, módulo 5, 2013. Fonte https://www.gov.br/anvisa/pt-br/centraisdeconteudo/publicacoes/servicosdesaude/publicacoes/modulo-5-tecnologias-em-servicos-de-saude-descricao-dos-meios-de-cultura-empregados-nos-exames-microbiologicos/@@download/file. PDF obtido 2026-11-08T09:57:05.171864-03:00; nova consulta local 2026-11-08T10:24:55.493522-03:00, America/Maceio. P. 7–8 e 11 (PDF 9–10 e 13): pesagem/hidratação e observância da instrução do fabricante. SHA-256 99821377c62d1d23f8598551e6c0d560c17869735fe482529cb34ab851363cee; original/extração preservados, ficha ANVISA-2013-M5-PREP-009.json. A introdução p. 8 menciona ciclo normalmente 121 °C/15 min e prioriza o rótulo/manual; não transformar isso em regra universal. Complementa a leitura de PREP-008: o trecho específico p. 15 não detalha ciclo, e a pergunta ao pesquisador permanece apropriada.

Derivação explícita: massa alvo = massa recomendada × volume alvo/volume de referência, mantendo a convenção declarada (volume de água ou final). Sem inferir proporção por marca, suplementos ou conservação. Documento/versão e consulta do fabricante são respostas do pesquisador, identificadas separadamente; o aplicativo não afirma ter consultado o documento particular. Manual federal candidato ao recorte, sem inclusão formal ou comprovação de edição mais recente. Imagem da balança US DEA reutilizada com origem/licença/hash e data original preservados.

## Esclarecimento de procedência — 2026-11-08T10:36:39.455394-03:00

Lucas exigiu que as fontes técnicas pertençam a um dos oito portais da tabela; não é obrigatório usar todos. Substitui a orientação de apenas priorizar. Fontes diretas EPSJV/IOC nos PREP-001 a PREP-006 permanecem preservadas, com regularização pendente. Anvisa e BVS MS já correspondem aos portais permitidos. Não alterar URLs de obtenção antigas nem afirmar acesso ao Arca sem confirmação.

Busca inicial de regularização: consultas web por título/Molinaro nos portais. Foi encontrada referência secundária ao handle Arca https://www.arca.fiocruz.br/handle/icict/13406 (capítulo de biossegurança); a tentativa de abrir não foi acessível pela ferramenta. Esse achado não comprova que os capítulos de química e diluição utilizados estejam disponíveis no Arca e não foi adicionado como fonte consultada dos protocolos. A busca e a conferência das fontes seguem pendentes.


## Regularização Arca — 2026-11-08T10:43:13.707165-03:00

Após falha da ferramenta web, acesso HTTP direto aos registros Arca confirmou os volumes usados. Busca por título/autor e navegação pelos registros da coleção, sem tratar uma referência secundária como prova.

Volume 1: https://www.arca.fiocruz.br/handle/icict/8658. PDF https://www.arca.fiocruz.br/bitstreams/dc35a81b-72c5-420f-9ff5-b3fe01f0c006/download. Obtido 2026-11-08T10:41:59.414205-03:00; consulta/conferência 2026-11-08T10:43:13.707165-03:00, America/Maceio. SHA-256 35206a3d5079758e26eaa6fcb343ead6aa7dac4674cbc6ec71d8015437e46b1c. Mesmo hash da cópia original FIOCRUZ-2009-vol1.pdf; nenhuma mudança de páginas ou cálculo. Registro HTML e PDF preservados, ficha ARCA-icict-8658-regularizacao.json.

Volume 4: https://www.arca.fiocruz.br/handle/icict/8661. PDF https://www.arca.fiocruz.br/bitstreams/62042256-afb7-4b93-b157-2cd5cc0a93d3/download. Obtido 2026-11-08T10:41:31.192083-03:00; consulta/conferência 2026-11-08T10:43:13.707165-03:00, America/Maceio. SHA-256 7d86374dd3be6d0e5196874cd510423f35fa96deb33e9fce2c08f4f39e6d0f8c. Mesmo hash da cópia original FIOCRUZ-volume4.pdf; nenhuma mudança de páginas ou cálculo. Registro HTML e PDF preservados, ficha ARCA-icict-8661-regularizacao.json.

Volume 4: divergência Arca 2009/ISBN versus copyright 2010 da cópia mantida explicitamente; ISBN não confirmado. Registro 13408 identificado como capítulo de química, mas não usado como cópia técnica: a fundamentação atual é o volume integral 8658. O lead 8659 corresponde ao volume 2, não ao volume 1 e não foi incorporado. Anvisa/BVS permanecem com procedência permitida. Fontes técnicas dos nove implementados agora têm registro/cópia nos portais admitidos, sem afirmar corpus final, última edição ou validação de bancada.


Regularização de fontes concluída: pacote `output/distribuicao/Planejador-Mac-PREP-001-a-009-fontes-regularizadas.zip` (82.720.131 bytes), com catálogo atualizado, nove POPs e pasta de registros. Assinatura ad hoc, igualdade do catálogo empacotado, CRC e presença dos nove POPs conferidos. Sessão Desktop e dados existentes preservados; sem repetir cliques no bundle ou testes Windows. Fonte regularizada não equivale à inclusão formal ou comprovação da edição mais recente.


## Consulta PREP-010 — 2026-11-08T10:51:07.891495-03:00

Consulta local de originais já obtidos nos portais permitidos, com inspeção visual: Anvisa módulo 5, 2013, p. 18 (PDF 20), e MS Guia Influenza, 2016, p. 48 (PDF 49). URLs: https://www.gov.br/anvisa/pt-br/centraisdeconteudo/publicacoes/servicosdesaude/publicacoes/modulo-5-tecnologias-em-servicos-de-saude-descricao-dos-meios-de-cultura-empregados-nos-exames-microbiologicos/@@download/file e https://bvsms.saude.gov.br/bvs/publicacoes/guia_laboratorial_influenza_vigilancia_influenza_brasil.pdf. Obtenções originais 2026-11-08T09:57:05.171864-03:00 e 2026-11-08T06:32:40.915588-03:00; nova consulta 2026-11-08T10:51:07.891495-03:00, America/Maceio. Hashes 99821377c62d1d23f8598551e6c0d560c17869735fe482529cb34ab851363cee e 0338bdad575528844378dc3fbc94533677e9a18458dffe281c3f791e0bcb0fb1, conferidos. Fichas específicas PREP-010 preservam origem, tempo e adaptação.

Ágar chocolate usa doses específicas distintas por recipiente; não transferir dose, temperatura, ciclo, sangue, cultivo ou validade para meios genéricos. Dimensionamento N×v e reserva percentual são derivações explícitas. Tipo de recipiente, dose, contagem e percentual perguntados ao pesquisador; formato/método ausentes ficam pendentes. Balão ilustrativo Hannes Grobe reutilizado com fonte/licença/hash/horário original. Não significa corpus final, última edição confirmada ou validação em bancada.


Pacote Mac PREP-001 a PREP-010: `output/distribuicao/Planejador-Mac-PREP-001-a-010.zip` (82.892.217 bytes), aplicativo, dez POPs e pasta de registros. Assinatura ad hoc, igualdade do catálogo empacotado, dez fichas com cálculo/fontes/imagem, recursos de equipamento e CRC do ZIP aprovados; sem banco de dados de usuário no pacote. Sessão Desktop preservada. Fluxo Qt de desenvolvimento inspecionado; sem repetir cliques no bundle ou testar Windows. Próxima entrega: integrar medições/estatística e exportações ao fluxo real dos dez protocolos, mantendo planejado e observado distintos.


## Integração de medições — 2026-11-08T11:07:39.590797-03:00

Integração de software: medições, resumo descritivo, comparação opcional e gráfico de pontos ligados ao fluxo real dos dez PREP e ao histórico SQLite. Dados observados não são calculados a partir do planejamento; rascunhos e análises têm estados distintos e vão aos arquivos de consulta. Reutilizados os métodos estatísticos existentes, sem nova consulta de fonte de protocolo nesta alteração. Evidências em docs/modulos/analise-estatistica.md.


## Preservação de gravação — 2026-11-08T11:21:55.089869-03:00

Correção de software na preservação de medições quando o histórico falha: cópia pendente independente, bloqueio de fechamento/arquivo/troca de protocolo e exportação de recuperação. Teste reproduziu o fechamento inseguro antes da correção. 295 testes completos aprovados; nenhum novo conteúdo científico de protocolo consultado nessa correção.


## Conferência de edições — 2026-11-08T11:28:23.275101-03:00

Busca dirigida Arca/Anvisa/BVS para as cinco obras dos dez PREP. Consulta API Arca por título retornou cinco volumes, preservada; índice Anvisa confirmou os módulos e nova obtenção dos três PDFs Anvisa/BVS resultou nos mesmos hashes usados no aplicativo. Não confundir volume, edição e postagem. Busca nativa BVS limitada, sem registros bibliográficos apresentados; ausência de edição posterior na busca dirigida não é prova universal.

Conferência visual do expediente do módulo 5, PDF p. 4: 1ª edição – 2010, copyright/ficha 2013; corrigida a descrição anterior “sem numeração indicada” no catálogo atual, preservando o registro anterior. Divergência de volume 4 permanece explícita. Nenhum cálculo ou página técnica alterado. Horários de novas obtenções, consultas, URLs, resultados e limites em docs/referencias/fontes/CONFERENCIA-EDICOES-20261108.json; inclusão formal no corpus não foi inventada.
