# Protocolos

Protocolos laboratoriais suportados pelo sistema.

Um protocolo é **dado**, não código: vive na tabela `protocolos` com seus
vínculos de reagente e material. Cadastrar um novo não exige alterar módulos —
ver [decisões](../decisoes/README.md).

> **Nenhum protocolo deve ser implementado antes de estar documentado aqui.**

Registro consolidado: [REGISTRO.md](../../REGISTRO.md). Atualizá-lo em cada nova consulta, extração ou inclusão, além da ficha individual.

## O que cada protocolo deve registrar

- nome do protocolo;
- área experimental;
- objetivo;
- variáveis de entrada;
- materiais necessários;
- reagentes necessários;
- volumes;
- concentrações;
- diluições;
- controles;
- repetições;
- etapas operacionais;
- limitações;
- referências.

## Proveniência obrigatória — instrução de Lucas em 30/10/2026

Cada protocolo adicionado deve ter um Markdown neste diretório, com **dia e
horário em que as informações foram obtidas e de onde foram retiradas**.
Isso inclui como executar, o que é necessário, quantidades, parâmetros,
fórmulas e limitações. Uma referência genérica no final não substitui a
identificação da origem de cada parte.

### Fontes prioritárias

Priorizar os portais informados na metodologia da revisão sistemática:
**Arca, BVS MS, Anvisa, Manuais SDA, Alice, Infoteca-e, eduCAPES e Oasisbr**.
O recorte documentado é de livros e manuais de instituições/órgãos federais
brasileiros, em português, desde 2000, com texto integral e edição mais recente
disponível até a busca. Conferir a metodologia vigente antes de executar buscas.

Estar num desses portais não torna uma obra automaticamente elegível. Registrar
o documento efetivamente consultado, sua instituição/autoria, título, edição,
ano, URL direta ou identificador persistente, seção e páginas. Registrar também
o portal pelo qual foi localizado.

Quando a informação não estiver nas fontes prioritárias, registrar a lacuna.
Se usar fonte técnica complementar, identificar essa condição e justificar o
uso. Não apresentar essa fonte como incluída na revisão sem atender aos
critérios metodológicos. O catálogo orienta a localização; para atribuir uma
regra ao documento original, é preciso consultar esse documento.

### Registro por fonte e por conteúdo

Para cada fonte, preencher:

| Campo | Registro obrigatório |
|---|---|
| ID da fonte | Identificador usado na ficha do protocolo |
| Documento | Autoria/instituição, título, ano e edição/versão |
| Localização | Portal de origem e URL direta/identificador do documento |
| Consulta/obtenção | Data e horário reais com fuso, em ISO 8601: `AAAA-MM-DDTHH:MM:SS-03:00`, indicando `America/Maceio` quando esse for o fuso utilizado |
| Local exato | Páginas, capítulo, seção ou tabela onde está a informação |
| Evidência | Caminho da cópia consultada, quando disponível, ou registro de acesso |
| Papel | Fonte elegível da revisão, elegibilidade pendente ou fonte técnica complementar |

Relacionar cada conteúdo à sua fonte e localização:

| Conteúdo extraído | ID da fonte | Página/seção | Consulta/obtenção | Adaptação para o software e justificativa |
|---|---|---|---|---|

Usar linhas separadas para procedimento, materiais/equipamentos, reagentes,
concentrações, volumes, controles, repetições, cálculos e limitações, conforme
aplicável. Se duas fontes forem combinadas, explicitar qual sustenta cada parte;
não apresentar a combinação como um protocolo integral de uma única fonte.

### Inclusão e atualizações

Registrar separadamente a data/hora de **inclusão no projeto**: ela pode ser
diferente da consulta/obtenção. Em toda atualização, acrescentar ao histórico
a data/hora, responsável, conteúdo alterado, fonte e motivo, preservando o
registro anterior. A data de publicação da obra também é um campo distinto.

Se o horário de uma consulta antiga não foi registrado, escrever **“não
registrado”**, sem usar o horário atual como se fosse o da obtenção. Identificar
referências ou trechos não conferidos como pendentes; não preencher lacunas por
suposição. Os dois exemplos do seed continuam demonstrativos até receberem
documentação real; esta regra não cria proveniência retroativa para eles.

## Tipos de protocolo

O campo `tipo` determina quais cálculos o sistema aplica ao gerar o plano:

| `tipo` | Cálculos aplicados |
|---|---|
| `preparo_solucao` | Escalonamento de reagentes e materiais |
| `diluicao` | Escalonamento; diluição simples ou seriada |
| `microplaca` | Escalonamento **e** organização de poços e placas |

Um `tipo` não reconhecido ainda gera plano com o escalonamento — apenas não
recebe os cálculos específicos.

## Protocolos cadastrados

Dois protocolos de exemplo são semeados automaticamente na primeira execução
(`backend/planejador/database/seed.py`), para que o sistema seja executável
imediatamente:

| Nome | Tipo |
|---|---|
| Preparo de solução salina 0,9% | `preparo_solucao` |
| Ensaio de crescimento em microplaca | `microplaca` |

São exemplos de demonstração. Protocolos reais do projeto devem ser documentados
neste diretório — um arquivo por protocolo — antes de serem cadastrados.

Ver [planejamento experimental](../modulos/planejamento-experimental.md) para
como o plano é gerado a partir de um protocolo.

## Dez candidatos P1 na interface

Selecionados em 30/10/2026 por serem preparações e cálculos básicos reutilizáveis. Disponíveis na busca por nome ou código, além dos dois exemplos. A seleção não equivale à implementação científica das dez rotinas.

| Código | Nome | Ficha |
|---|---|---|
| PREP-001 | Preparo de soluções percentuais (% m/v, v/v e variações aplicáveis) | [PREP-001](PREP-001.md) |
| PREP-002 | Preparo de soluções molares | [PREP-002](PREP-002.md) |
| PREP-003 | Preparo de solução-estoque | [PREP-003](PREP-003.md) |
| PREP-004 | Diluição de solução-estoque | [PREP-004](PREP-004.md) |
| PREP-005 | Diluição seriada / sucessiva | [PREP-005](PREP-005.md) |
| PREP-006 | Cálculo de fator de diluição e concentração final | [PREP-006](PREP-006.md) |
| PREP-007 | Cálculo de volume total e percentual excedente | [PREP-007](PREP-007.md) |
| PREP-008 | Preparo de meio a partir de formulação | [PREP-008](PREP-008.md) |
| PREP-009 | Preparo de meio comercial desidratado | [PREP-009](PREP-009.md) |
| PREP-010 | Cálculo de meio necessário por número de placas/tubos | [PREP-010](PREP-010.md) |
