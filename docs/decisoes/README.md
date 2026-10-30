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
