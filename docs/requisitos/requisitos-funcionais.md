# Requisitos funcionais

O que o sistema deve fazer. A coluna **Estado** reflete o código em
`backend/planejador/` — o backend está implementado; a interface, não.

## Planejamento experimental

| # | Requisito | Estado | Onde |
|---|---|---|---|
| RF01 | Permitir seleção de protocolo experimental | Implementado | `services/experimento_service.py` (`listar_protocolos`) |
| RF02 | Permitir entrada de variáveis do experimento | Implementado | `services/planejamento_service.py` |
| RF03 | Gerar cálculos operacionais automaticamente | Implementado | `core/calculos.py` |
| RF04 | Gerar lista de reagentes | Implementado | `services/planejamento_service.py` |
| RF05 | Gerar lista de materiais | Implementado | `services/planejamento_service.py` |
| RF06 | Gerar volumes | Implementado | `core/calculos.py` |
| RF07 | Gerar concentrações | Implementado | `core/calculos.py` |
| RF08 | Gerar diluições | Implementado | `core/calculos.py` |
| RF09 | Gerar organização experimental | Implementado | `core/calculos.py` (tubos e microplaca) |
| RF10 | Gerar plano operacional para execução | Implementado | `services/planejamento_service.py` |

## Registro e organização dos dados

Etapas do fluxo entre a execução na bancada e a análise.

| # | Requisito | Estado | Onde |
|---|---|---|---|
| RF17 | Registrar os dados experimentais obtidos | Implementado | `services/experimento_service.py` |
| RF18 | Organizar os dados em tabelas estruturadas | Implementado | `core/tabelas.py` |
| RF19 | Disponibilizar os resultados para fora do app | Implementado | `services/estatistica_service.py` (CSV) |

## Análise estatística

| # | Requisito | Estado | Onde |
|---|---|---|---|
| RF11 | Calcular média | Implementado | `core/estatistica.py` |
| RF12 | Calcular desvio padrão | Implementado | `core/estatistica.py` |
| RF13 | Calcular variância | Implementado | `core/estatistica.py` |
| RF14 | Executar teste t | Implementado | `core/estatistica.py` |
| RF15 | Executar ANOVA (uma via) | Implementado | `core/estatistica.py` |
| RF16 | Gerar gráficos | Pendente | depende da interface |

## Requisitos futuros

Expansão de escopo prevista, sem prazo definido:

- Suporte a química.
- Suporte a fenólicos.
- Suporte a flavonoides.
- Suporte a antioxidantes.
- Suporte a ensaios biológicos.
- Cadastro de novos protocolos experimentais pela interface.

Ver [visão geral](../visao-geral.md) para o escopo completo e
[decisões](../decisoes/README.md) para as escolhas técnicas.
