# Visão do sistema

Retrato de alto nível de como as partes se encaixam. Para o detalhe de cada
camada, ver [backend](backend.md) e [banco de dados](banco-de-dados.md).

## Partes

```
┌─────────────────────────────────────────────────┐
│  Interface (PyQt6)          — não implementada   │
│  API HTTP (FastAPI)         — opcional           │
└───────────────────────┬─────────────────────────┘
                        │  chamadas diretas de função
┌───────────────────────▼─────────────────────────┐
│  services/   orquestra e devolve tipos simples   │
└──────────┬──────────────────────────┬───────────┘
           │                          │
┌──────────▼───────────┐  ┌───────────▼───────────┐
│  core/               │  │  database/            │
│  cálculo puro         │  │  SQLAlchemy + SQLite  │
│  sem banco, sem UI    │  │  todo o SQL isolado   │
└──────────────────────┘  └───────────┬───────────┘
                                      │
                          ┌───────────▼───────────┐
                          │  planejador.db        │
                          └───────────────────────┘
```

## Regra de dependência

As dependências apontam **apenas para baixo**: `ui/api → services → core / database`.

Nenhum módulo de `core/` importa `database/`, e nenhum dos dois conhece a
interface. Isso é o que permite validar os cálculos isoladamente contra conta
feita à mão, sem subir banco nem tela.

## Fluxo de uma requisição

Planejar um experimento (`gerar_plano`):

1. A interface entrega protocolo escolhido e parâmetros ao service.
2. O service pede ao `repositories` os reagentes e materiais do protocolo.
3. Passa cada `quantidade_base` por `calculos.escalonar_quantidade`.
4. Se o protocolo for do tipo `microplaca`, chama `calculos.planejar_microplaca`.
5. Devolve um `PlanoOperacional` — dataclass simples, sem objetos do ORM.

Analisar dados (`analisar_experimento`):

1. O service carrega as medições agrupadas do banco.
2. Calcula o resumo descritivo de cada grupo.
3. Escolhe o teste conforme o número de grupos: 2 → teste t, 3+ → ANOVA.
4. Devolve um dicionário serializável.

## Dois modos de integração

A interface desktop chama os **services diretamente**, como funções Python — não
há HTTP no caminho, nem servidor para subir.

A camada `api/` (FastAPI) existe para o caso de um frontend web ou uma
integração externa. É opcional: instala-se com o extra `api` e nada no restante
do sistema muda.

## Escolhas que moldam o desenho

Protocolos são **dados**, não código — adicionar um protocolo é inserir linhas
no banco, não escrever um módulo novo. É o que sustenta a expansão prevista para
química, fenólicos e ensaios biológicos sem reescrever o núcleo.

O banco é trocável por variável de ambiente, sem alterar código. Ver
[decisões](../decisoes/README.md).
