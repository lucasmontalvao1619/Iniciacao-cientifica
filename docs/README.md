# Documentação

Fonte oficial de contexto do projeto. Cada pasta cobre um tema; o `README.md`
de cada uma é a porta de entrada daquele tema.

## Por onde começar

1. [Visão geral](visao-geral.md) — objetivo, escopo e funcionalidades esperadas.
2. [Requisitos](requisitos/) — o que o sistema deve fazer e sob quais restrições.
3. [Decisões](decisoes/) — escolhas técnicas e suas justificativas.
4. [Arquitetura](arquitetura/) — como o sistema é construído.

Registro de origem e datas dos protocolos: [REGISTRO](../REGISTRO.md).

## Mapa

| Pasta | Conteúdo |
|---|---|
| [`arquitetura/`](arquitetura/) | [Visão do sistema](arquitetura/visao-do-sistema.md), [backend](arquitetura/backend.md), [banco de dados](arquitetura/banco-de-dados.md), [frontend](arquitetura/frontend.md) |
| [`requisitos/`](requisitos/) | [Funcionais](requisitos/requisitos-funcionais.md), [não funcionais](requisitos/requisitos-nao-funcionais.md), [casos de uso](requisitos/casos-de-uso.md) |
| [`modulos/`](modulos/) | [Planejamento experimental](modulos/planejamento-experimental.md), [análise estatística](modulos/analise-estatistica.md) |
| [`decisoes/`](decisoes/) | Registro de decisões técnicas, científicas e arquiteturais |
| [`protocolos/`](protocolos/) | Protocolos laboratoriais e o que cada um deve documentar |
| [`formulas/`](formulas/) | Fórmulas laboratoriais e estatísticas |
| [`referencias/`](referencias/) | Bibliografia e material de apoio |

## Estado do projeto

O **backend está implementado** (cálculos, estatística, banco, services e API
opcional), com testes automatizados. A **interface PyQt6 tem uma primeira prévia navegável** —
ver [frontend](arquitetura/frontend.md).

Prévia e fluxo: [interface](interface/README.md).

Aplicativo macOS: [distribuição](distribuicao/README.md).

## Fora desta pasta

- `backend/README.md` — como instalar, ligar o banco e executar.
- `AGENTS.md` — instruções para agentes de IA que trabalham no repositório.
- `Análise de dados IC/` — vault do Obsidian; memória de longo prazo do projeto.

## Convenções

- Documentar antes de implementar: protocolos e fórmulas entram aqui primeiro.
- Toda decisão arquitetural relevante vai para [`decisoes/`](decisoes/).
- Um tema por pasta; nada de arquivo solto duplicando o que já está numa pasta.
