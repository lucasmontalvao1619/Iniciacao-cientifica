# Requisitos não funcionais

Restrições e qualidades esperadas do sistema.

## Arquitetura

| # | Requisito | Como é atendido |
|---|---|---|
| RNF01 | Seguir arquitetura modular | Camadas `core` / `database` / `services` / `api`, com dependências apenas "para baixo". Ver [arquitetura do backend](../arquitetura/backend.md) |
| RNF02 | Permitir expansão para novos protocolos | Protocolos são dados no banco, não código: incluir um protocolo é inserir linhas, não alterar módulos |
| RNF03 | Permitir expansão para novas áreas experimentais | O núcleo de cálculo é agnóstico de área; a área vive no campo `tipo` do protocolo |

## Qualidade e manutenção

| # | Requisito | Como é atendido |
|---|---|---|
| RNF04 | Cálculos verificáveis | Funções puras em `core/`, sem banco nem UI, validáveis contra cálculo manual |
| RNF05 | Cobertura por testes automatizados | `pytest` sobre SQLite em memória, sem tocar no banco real |
| RNF06 | Tipagem e padronização de código | `mypy` (tipos) e `ruff` (lint e formatação), configurados em `pyproject.toml` |
| RNF07 | Erros compreensíveis ao usuário | Exceções de domínio em `core/exceptions.py`, com mensagem e dica, tratadas na borda (UI/API) |

## Portabilidade e segurança

| # | Requisito | Como é atendido |
|---|---|---|
| RNF08 | Independência de motor de banco | SQLAlchemy; trocar de SQLite para Postgres/MySQL só muda `APP_DATABASE_URL` |
| RNF09 | Execução local sem servidor | SQLite por padrão — um arquivo, sem instalação nem credenciais |
| RNF10 | Nenhuma credencial no código | Configuração lida de variáveis de ambiente (ver `.env.example`) |
| RNF11 | Proteção contra SQL injection | Acesso exclusivamente via repositórios com ORM e parâmetros vinculados |
| RNF12 | Reprodutibilidade | Dependências fixadas em `pyproject.toml`; banco recriável por `python -m planejador.bootstrap` |

Justificativas das escolhas em [decisões](../decisoes/README.md).
