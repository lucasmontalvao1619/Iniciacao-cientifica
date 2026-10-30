# Iniciação Científica

## Problema

Pesquisadores e estudantes precisam planejar experimentos laboratoriais com cálculos operacionais, reagentes, materiais, volumes, concentrações, diluições, controles, repetições e organização experimental. Esse processo pode ser demorado, repetitivo e sujeito a erros.

## Visão geral

Este projeto propõe um aplicativo para planejamento automático de experimentos laboratoriais e análise estatística de dados experimentais.

O sistema deverá permitir selecionar protocolos, informar variáveis experimentais e gerar um plano operacional para execução do experimento.

## Módulos previstos

- Planejamento experimental.
- Protocolos laboratoriais.
- Cálculos operacionais.
- Reagentes e materiais.
- Organização experimental.
- Registro e organização dos dados experimentais.
- Análise estatística.
- Geração de gráficos.

## Tecnologias

- Python (>=3.11).
- PyQt6 (interface — ainda não implementada).
- SQLite via SQLAlchemy (banco atual; Postgres/MySQL plugáveis por configuração).
- NumPy, Pandas, SciPy, Matplotlib (cálculos e estatística).

## Estrutura de diretórios

```
Iniciacao-cientifica/
├── backend/planejador/     # backend da aplicação (implementado)
│   ├── core/               # cálculos, estatística e tabelas — sem banco, sem UI
│   ├── database/           # acesso a dados (SQLAlchemy)
│   ├── services/           # planejamento, experimentos e estatística
│   ├── api/                # API HTTP opcional (FastAPI)
│   ├── config.py           # configuração via variáveis de ambiente
│   └── bootstrap.py        # cria tabelas e semeia dados de exemplo
├── frontend/               # interface PyQt6 — ainda não implementada
├── database/               # schema.sql (referência do modelo) e seed.sql
├── docs/                   # documentação, organizada por tema
├── tests/                  # testes do backend (pytest)
├── .claude/skills/         # skills do Claude Code adaptadas ao projeto
├── Análise de dados IC/    # vault do Obsidian (notas do projeto)
├── pyproject.toml          # dependências, ruff, mypy, pytest
├── Makefile                # atalhos: make help
└── .env.example            # variáveis de ambiente documentadas
```

Dependências apontam só para baixo: `ui/api → services → core / database`.

Para instalar e executar o backend, ver `backend/README.md`. Para navegar a
documentação, começar por `docs/README.md`.

## Fluxo de desenvolvimento

1. Documentar requisitos, protocolos, fórmulas e decisões.
2. Definir arquitetura modular.
3. Modelar banco de dados.
4. Planejar implementação.
5. Implementar mediante pedido explícito (backend já implementado; frontend
   PyQt6 é a próxima etapa).
