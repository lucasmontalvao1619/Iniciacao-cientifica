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
| Interface | PyQt6 (prevista, ainda não implementada) |
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
