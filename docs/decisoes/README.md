# Decisões

Registro das escolhas técnicas, científicas e arquiteturais do projeto, com as
respectivas justificativas.

Novas decisões devem ser registradas aqui **antes ou durante** a implementação.
Decisões registradas não devem ser contrariadas sem que este documento seja
atualizado.

## Decisões vigentes

| Tema | Decisão |
|---|---|
| Linguagem | Python (>= 3.11) |
| Plataforma principal | Windows desktop nativo; macOS secundário |
| Interface | PyQt6 (primeira prévia de planejamento implementada) |
| Banco de dados | SQLite por padrão, via SQLAlchemy, agnóstico de motor |
| Acesso a dados | SQLAlchemy (ORM), isolando o SQL do restante do app |
| Arquitetura | Modular: `core` / `database` / `services` / `api` / `ui` |
| Foco inicial | Microbiologia |

## Banco de dados: SQLite via SQLAlchemy (2026-07-18)

**Contexto.** A proposta original mencionava "MySQL", mas o requisito real é o
uso da **linguagem SQL** — não de um servidor específico.

**Decisão.** Adotar SQLite acessado via SQLAlchemy.

**Justificativa.** Para um protótipo de iniciação científica — aplicativo
desktop, um usuário, execução local, com reprodutibilidade como meta:

- Liga sem servidor nem credenciais (um arquivo local): facilita "ligar o banco".
- Reprodutibilidade: o banco acompanha o projeto; a banca executa imediatamente.
- Sem custo, latência ou dependência de rede — evita cloud desnecessária.
- Portabilidade: por usar SQLAlchemy, migrar para PostgreSQL ou MySQL exige
  apenas alterar a variável `APP_DATABASE_URL`; o código de acesso não muda.

**Consequências.** PostgreSQL, MySQL ou cloud passam a fazer sentido se o
sistema evoluir para multiusuário ou web — e a troca já está preparada. Os
extras `postgres` e `mysql` do `pyproject.toml` instalam os drivers necessários.

Ver [banco de dados](../arquitetura/banco-de-dados.md) para o modelo e
`.env.example` para a configuração.

## Protocolos como dados, não como código

**Decisão.** Um protocolo é uma linha no banco com seus vínculos de reagente e
material — não um módulo Python.

**Justificativa.** O escopo futuro prevê expansão para química, fenólicos,
flavonoides, antioxidantes e ensaios biológicos. Se cada protocolo fosse código,
cada expansão exigiria alterar o núcleo. Como dados, adicionar um protocolo é
inserir linhas.

**Consequências.** O campo `tipo` do protocolo decide quais cálculos se aplicam.
Cadastrar protocolos pela interface é um requisito futuro.

## Unidades ficam a cargo de quem chama

**Decisão.** As funções de `core/calculos.py` são agnósticas de unidade: exigem
apenas coerência entre as entradas.

**Justificativa.** Mantém o núcleo simples e testável. A unidade de cada
reagente já está no banco, no campo `unidade`.

**Consequências.** Cabe à camada superior (services/UI) garantir que as unidades
combinam. Conversão automática de unidades não está implementada.

## Prévia da interface (2026-10-30)

Quatro telas PyQt6 baseadas em UC01–UC06, chamando services diretamente. O seed usa SQLite em memória isolado, sem tocar no banco real. Exportação JSON identifica conteúdo demonstrativo e fonte científica ausente. Fontes/versões e integração com dados persistentes ficam para o ciclo seguinte; não há validação para bancada nesta prévia.

## Interface: planejamento, análise e gráficos (2026-10-30)

Manter uma aplicação desktop única com duas áreas: o fluxo de planejamento sequencial e análise/plotagem de medições. Reusar `analisar_grupos`, com Matplotlib embutido no Qt; inferência desativada inicialmente e habilitada explicitamente. Guardar planejamento separado de observações. Instância única via QLockFile; não muda banco ou camada de cálculos.

## Processo único: do planejamento aos resultados (2026-10-30)

A pedido de Lucas, esta revisão substitui as duas áreas independentes por uma navegação sequencial única: Início, Protocolo, Parâmetros, Plano, Resultados. Resultados depende do plano válido e recebe sua identificação, protocolo e organização; os valores observados são inseridos pelo usuário, sem preenchimento a partir de parâmetros planejados. Mudança de planejamento invalida o contexto, as medições e análises anteriores para não misturar experimentos.

A entrada de medições usa uma tabela por grupo e unidade informada pelo usuário. Estatística descritiva e gráfico são o caminho padrão; teste t/ANOVA permanecem como comparação opcional, nas opções avançadas, sem pressupor independência das replicatas. A exportação JSON pode reunir plano, parâmetros, valores observados e análise; o PNG é o gráfico do experimento identificado. Ainda não é persistência de medições no banco pela UI.

O dropdown editável abre sugestões ao clicar no próprio campo; permanece pesquisável por nome/código sem acentos, com primitives Qt e navegação por teclado. Não há área de pesquisa separada.

## Windows como prioridade (2026-10-30)

Instrução explícita de Lucas: priorizar Windows em interface, testes, instalação e distribuição nativa `.exe`, mantendo macOS como suporte secundário. PyQt6 permanece como tecnologia multiplataforma. A compilação macOS já produzida é uma prévia secundária; teste real do executável Windows permanece necessário antes de declarar a entrega Windows validada.

A proveniência dos protocolos é centralizada em `REGISTRO.md` na raiz, com ligação às fichas. Horários existentes de consulta ao catálogo não são horários de leitura das fontes primárias.

## Implementação dos dez PREP (2026-11-08)

Lucas confirmou manter o recorte federal brasileiro em português desde 2000. Implementar PREP-001 a PREP-010 sequencialmente, com parâmetros específicos, cálculo verificável, POP/DOCX ilustrado e proveniência por conteúdo. Retirar linguagem demonstrativa da interface sem apresentar protocolos incompletos como implementados. Resultados calculados devem permitir edição com recálculo e gráfico quando aplicável; medições observadas continuam distintas de resultados planejados.

Histórico local limitado a dez experimentos. Excedentes e itens retirados devem ir para `Registros de Experimentos` para consulta/exportação; Lucas escolheu não reabrir como sessão. Distribuição Windows nativa e macOS, com a pasta de registros no ZIP. Não declarar Windows entregue sem executável e teste real. Nenhuma simplificação adicional dos Markdown foi autorizada: apresentar sugestões antes de remover conteúdo não redundante.

## Variáveis perguntadas ao pesquisador (08/11/2026)

Lucas pediu que variáveis fossem apresentadas como perguntas ao pesquisador, favorecendo uso por diferentes laboratórios. A interface exige as propriedades numéricas que entram no cálculo escolhido, sem presumir valores como pureza de 100%; identificação de substância, lote e responsável são opcionais no planejamento. Para estoque, dados de rótulo e conservação ausentes permanecem pendentes, sem prazo de validade calculado automaticamente. Essas informações não se confundem com a proveniência das regras científicas, que permanece registrada.

## Restrição dos portais das fontes técnicas (08/11/2026)

Lucas esclareceu: não é necessário utilizar todos os portais, mas toda fonte técnica usada para fundamentar os protocolos deve ser obtida ou ter seu registro confirmado em pelo menos um destes: Arca/Fiocruz, BVS MS, Central de Conteúdo/Publicações da Anvisa, Manuais SDA, Alice, Infoteca-e, eduCAPES ou Oasisbr. Ser uma instituição federal, isoladamente, não substitui esse requisito de procedência. Manter português, publicação desde 2000 e demais critérios da metodologia.

Os livros Fiocruz v. 1 e v. 4 foram obtidos diretamente na EPSJV/IOC, fora desses portais. Seus registros/cópias/extrações são preservados, mas a adequação da procedência permanece pendente: localizar registro/cópia em portal permitido ou substituir a fundamentação por fonte elegível, conferindo novamente as regras afetadas. Não trocar apenas a URL nem inventar acesso ao Arca. Esta decisão supera a orientação anterior de apenas priorizar os portais.

Rótulos e receitas particulares declarados pelo pesquisador são dados de entrada, não obras incluídas no corpus nem substitutos das fontes elegíveis para justificar as regras do programa. Sua origem deve continuar identificada separadamente.


## Regularização confirmada — 2026-11-08T10:43:13.707165-03:00

Pendência de procedência dos PREP-001 a PREP-006 resolvida: downloads efetivos dos volumes 1 e 4 no Arca, comparados byte a byte com as cópias anteriores. Catálogo identifica novos acessos sem apagar os antigos. Ver [evidências e limites](../referencias/REGULARIZACAO_FONTES.md). A inclusão formal e a edição mais recente continuam sem comprovação; divergência bibliográfica do volume 4 preservada.


## Integração de medições — 2026-11-08T11:07:39.590797-03:00

Medições dos dez PREP passam a usar o AnalysisWidget existente dentro de Resultados, recolhido inicialmente; planejamento e observações continuam separados. Rascunhos e análises são persistidos no mesmo registro local e preservados em arquivos de consulta. Mudanças no planejamento limpam as observações da sessão. Detalhes em [análise estatística](../modulos/analise-estatistica.md).


## Disponibilidade do Windows — 2026-11-08T18:45:43.747607-03:00

Lucas informou acesso ao PC Windows, ao lado do Mac. A compilação/teste deixam de estar adiados por indisponibilidade do PC; o controle deste chat permanece no Mac. Preparado pacote fonte para transferência e execução da receita no Windows, sem substituir os arquivos do projeto que possam existir lá. Só afirmar exe gerado/testado após evidência dessa execução.


## Instalação e testes pelo GitHub — 08/11/2026

Lucas priorizou concluir o aplicativo e usar GitHub para compilar/testar Windows, com downloads Mac/Windows no repositório. Windows terá instalador Inno Setup por usuário, incluindo dependências e atalhos, além do ZIP portátil; não exigir Python do usuário final. Pipeline deve conferir código e executável empacotado antes da publicação, e testar instalação/desinstalação preservando registros. A validação clínica/bancada e a revisão formal não são inferidas desses testes.


## Resultados por etapas — 08/11/2026

A pedido de Lucas: resumo calculado aparece primeiro; ajustar parâmetros e visualizar simulação são expansões opcionais. Figuras/canvas carregam somente ao solicitar visualização/análise. Medições usam colunas por valor e colagem tabular Excel; strings antigas com ponto e vírgula continuam legíveis. Comparação exige respostas explícitas sobre independência e pressupostos, sem acrescentar testes ou interpretar significância como eficácia. Plano e observações mantêm vínculo e regras de invalidação/preservação existentes.
