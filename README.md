# Iniciação Científica

## Baixar o aplicativo

| Plataforma | Download |
|---|---|
| **Windows 64 bits** | [**Baixar para Windows — instalador**](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/releases/latest/download/Planejador-Windows-Setup.exe) |
| **Mac com Apple Silicon** | [**Baixar para Mac**](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/releases/latest/download/Planejador-Mac.zip) |

No Windows, abra o instalador: ele inclui as dependências e cria os atalhos. Não precisa instalar Python nem executar comandos. No Mac, extraia o ZIP e abra o aplicativo. Os dez POPs acompanham a instalação.

[Versão portátil do Windows](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/releases/latest/download/Planejador-Windows-Portatil.zip) · [Todas as versões](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/releases) · [Testes e compilações](https://github.com/lucasmontalvao1619/Iniciacao-cientifica/actions)

Os pacotes só são publicados após os testes automatizados, a compilação nativa e a verificação do executável. O instalador Windows também passa por instalação/desinstalação automatizada, preservando um registro de teste. Isso não substitui avaliação em bancada ou testes manuais de interface.


## Organização local no Mac

A pasta `~/Desktop/INICIACAO CIENTIFICA` é a entrada do pesquisador: aplicativo, POPs, registros, pesquisa e instaladores. O código-fonte fica em `Desenvolvimento/` (este repositório). Ver [mapa e conferência da organização](docs/distribuicao/ORGANIZACAO_LOCAL.md).

## Problema

Pesquisadores e estudantes precisam planejar experimentos laboratoriais com cálculos operacionais, reagentes, materiais, volumes, concentrações, diluições, controles, repetições e organização experimental. Esse processo pode ser demorado, repetitivo e sujeito a erros.

## Visão geral

Aplicativo desktop para planejamento de experimentos laboratoriais e análise estatística de dados experimentais.

O sistema implementa dez protocolos PREP, com parâmetros próprios, planos calculados, POPs ilustrados, medições, estatística e gráficos.

O fluxo liga o plano à coleta: gere o modelo Excel, registre observações reais, importe com prévia e consulte o resumo e os gráficos. Também é possível importar planilhas existentes e escolher cabeçalhos/colunas. A opção **Como usar**, dentro do aplicativo, explica o percurso; [critérios e evidências da entrega](docs/modulos/CONCLUSAO_APLICATIVO.md) registram os limites e as verificações.

## Módulos implementados

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
- PyQt6 (interface desktop de planejamento e resultados).
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
├── frontend/               # interface PyQt6 de planejamento e análise
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
   PyQt6 implementado em `frontend/`).

## Executar a partir do código

Na raiz: `.venv/bin/python -m frontend.app`. Instalação: `pip install -e ".[ui]"`. Ver [fluxo e auditoria](docs/interface/README.md).

## Aplicativo no macOS

Nome do aplicativo: **Planejador de Experimentos**. Empacotamento e instruções em [distribuição macOS](docs/distribuicao/README.md). Abrir o bundle `.app` no Desktop dispensa o terminal.

## Plataforma prioritária e registro de fontes

**Windows é o alvo principal**, com aplicativo desktop nativo e distribuição `.exe`; macOS é secundário. A compilação macOS existente não comprova validação em Windows. Consulte [distribuição](docs/distribuicao/README.md).

A origem, dia e horário disponíveis para os protocolos estão em [REGISTRO.md](REGISTRO.md). Consultas ao catálogo e consultas às fontes primárias são identificadas separadamente.
