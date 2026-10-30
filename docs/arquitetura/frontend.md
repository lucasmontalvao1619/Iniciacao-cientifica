# Frontend

**Estado: primeira prévia implementada.** `frontend/app.py` cobre início, seleção, parâmetros e revisão do plano usando services e seed em memória. Ver [fluxo e auditoria](../interface/README.md). A interface também recebe medições em memória para estatística e gráfico de pontos; persistência das medições pela UI ainda está pendente.

## Tecnologia prevista

PyQt6, aplicação desktop de usuário único, rodando localmente.

## Como deve conversar com o backend

A interface chama os **services diretamente**, como funções Python:

```python
from planejador.services import gerar_plano, analisar_grupos
```

Não é preciso subir servidor nem falar HTTP. A camada `api/` (FastAPI) existe
apenas para frontends web ou integrações externas — a UI desktop a ignora.

Os services devolvem dataclasses e dicionários simples (`PlanoOperacional`,
relatório estatístico), sem objetos do ORM vazando. São diretos de mapear para
uma `QTableWidget` ou modelo Qt.

## Responsabilidades da camada

A UI **não** faz cálculo nem SQL. Ela deve:

- coletar entrada do usuário e validar formato (campo vazio, texto onde se
  espera número);
- chamar o service adequado;
- capturar `ErroPlanejamento` (base de `EntradaInvalida` e
  `RegistroNaoEncontrado`) e exibir a mensagem ao usuário — quando a exceção for
  `EntradaInvalida`, mostrar também o atributo `dica`, que traz a sugestão de
  correção;
- apresentar resultados em tabela e gráfico.

A validação de **regra** (concentração final maior que a inicial, número de
replicatas menor que 1) já é feita no `core` e chega como exceção com mensagem
pronta para exibir — a UI não deve duplicar essas checagens.

## Telas previstas

| Tela | Função | Service |
|---|---|---|
| Seleção de protocolo | Listar protocolos cadastrados | `repositories.listar_protocolos` |
| Parâmetros do experimento | Amostras, replicatas, controles, excesso | — |
| Plano operacional | Reagentes, materiais e microplaca calculados | `gerar_plano` |
| Registro de medições | Entrada de valores por grupo | `repositories` |
| Análise estatística | Resumo, teste t / ANOVA e gráficos | `analisar_grupos` |

## Gráficos

Matplotlib embutido no Qt (`FigureCanvasQTAgg`). É o único requisito funcional
ainda pendente (RF16) — depende desta camada, já que os dados que o alimentam
(`resumo`, `teste_t`, `anova_uma_via`) estão prontos no `core`.

## Ponto de partida

`planejador.bootstrap.iniciar()` deve ser chamado uma vez ao subir a aplicação:
cria as tabelas e semeia dados de exemplo. É idempotente.
