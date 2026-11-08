# PREP-007 — Volume total e percentual excedente

## Implementação de 08/11/2026

Perguntas: unidade de volume (µL, mL, L), volume por unidade v, total de unidades N e percentual E acrescentado à base. N já inclui controles e repetições pertinentes; não multiplicar novamente. Identificação do material é livre/opcional. Volume e número de unidades começam sem resposta; excedente zero é apresentado como ausência de reserva, sem adotar margem positiva automática.

Vbase=v×N; reserva=Vbase×E/100; Vtotal=Vbase×(1+E/100). O percentual é acréscimo sobre a base, não fração perdida do total preparado. Mudar unidade não converte números automaticamente. Todas as quantidades são expressas na unidade selecionada. N inteiro de 1 a 1000000 na interface; v positivo, E não negativo, entradas/resultados finitos.

Fonte: Ministério da Saúde, Guia para a Rede Laboratorial de Vigilância de Influenza no Brasil, 1ª edição eletrônica, 2016, p. impressa 48 (PDF 49), BVS MS, ISBN 978-85-334-2402-9. A obra demonstra dimensionamento por número de reações e reserva por perdas. A calculadora percentual é uma adaptação matemática explícita, sem aplicar universalmente a regra específica +1/+2 reações do guia. Fonte candidata ao recorte, sem inclusão formal ou comprovação de edição mais recente.

Original/extração, fonte, edição, página, hash e horários reais com fuso em [REGISTRO.md](../../REGISTRO.md) e MS-2016-INFLUENZA-PREP-007.json. Imagem complementar de micropipeta: Emicropipette, CC BY-SA 4.0, URL/hash/data registrados em frontend/assets/equipment/micropipeta.json e no POP; sem preferência obrigatória de marca/modelo.

Plano/Resultados mostram base, reserva e total. Edição atualiza gráfico comparativo por número de unidades e o mesmo registro do histórico. O gráfico usa no máximo 21 pontos mesmo para um milhão de unidades. A reserva não aumenta a dose por unidade. Não determina composição, concentração, estabilidade, perdas medidas nem tolerância de equipamento; sem validação em bancada.

237 testes passaram na suíte completa, com contas independentes, zero excedente, inválidos, tipos/finitude/estouro, unidades, recálculo, histórico e exportações. Ruff e mypy core/service com imports omitidos aprovados; não é tipagem completa das dependências. DOCX ilustrado renderizado e conferido em duas páginas, capturas Qt inspecionadas e página de 880 px sem rolagem horizontal.

Pacote Mac PREP-001-a-007 gerado com sete POPs e pasta de registros; assinatura, catálogo e integridade conferidos. Windows ainda não executado.

## Registro anterior preservado

# PREP-007 — Cálculo de volume total e percentual excedente

**Estado:** candidato P1 selecionado para a lista da interface; não é ficha operacional validada nem cálculo específico implementado.

## Origem e datas

- Consulta do catálogo local e inclusão: 2026-10-30T04:56:36-03:00 (`America/Maceio`).
- Fonte consultada: F03, Catálogo de Priorização, v1.0, agosto/2026, tabela de preparações, linha PREP-007.
- Documento: https://docs.google.com/document/d/1n9e8ClML7KyyJG15ZkhF8hbG9_zWbPzu/edit
- Evidência de importação: `frontend/protocolos.json`, registro PREP-007, extraído de `contexto/catalogo_protocolos.json` do acervo analisado anteriormente.
- Fontes apontadas pelo catálogo: B5 — Microbiology Society.
- Data/hora de consulta às fontes primárias: **não registrada**. As referências apontadas não foram consultadas nesta inclusão.

## Seleção

Rotina básica de preparo/cálculo, com potencial de reutilização no núcleo comum e menor dependência de interpretação de ensaios microbiológicos. A inclusão na lista é uma escolha de desenvolvimento de Lucas, não inclusão automática no corpus da revisão.

## Pendências para cálculo operacional

Conferir fonte integral, edição, páginas, finalidade, procedimento, materiais/reagentes, unidades, entradas, fórmulas, controles e limitações pertinentes. Registrar a origem de cada trecho antes da implementação. Priorizar as fontes da metodologia da revisão, começando por Anvisa quando aplicável; as demais referências são complementares até avaliação de elegibilidade.

Nenhuma instrução de bancada ou quantidade foi criada por suposição. Ver a regra de proveniência em `README.md` desta pasta.
