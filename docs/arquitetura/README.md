# Arquitetura

Como o sistema é construído.

| Documento | Conteúdo |
|---|---|
| [Visão do sistema](visao-do-sistema.md) | Retrato de alto nível, regra de dependência entre camadas e fluxo de uma requisição |
| [Backend](backend.md) | Camadas `core`, `database`, `services` e `api` em detalhe |
| [Banco de dados](banco-de-dados.md) | Motor, modelo de dados, arquivos e segurança |
| [Frontend](frontend.md) | Primeira prévia PyQt6 do planejamento e decisões de integração |

## Princípio central

Dependências apontam apenas "para baixo": `ui/api → services → core / database`.

O núcleo de cálculo não conhece banco nem interface — é o que permite validá-lo
contra conta feita à mão.

Justificativas das escolhas em [decisões](../decisoes/README.md); instruções de
execução em `backend/README.md`.
