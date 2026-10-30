# Backend — Planejador de Experimentos

Backend e banco de dados do aplicativo. Código Python organizado em camadas,
com SQLite por padrão (via SQLAlchemy) e troca fácil para Postgres/MySQL.

## Estrutura

```
backend/planejador/
├── config.py          # configurações (lê APP_DATABASE_URL do ambiente)
├── bootstrap.py       # "liga tudo": cria tabelas + dados de exemplo
├── core/              # cálculos e estatística (puros, sem banco/UI)
│   ├── calculos.py    # diluição, massa, escalonamento, tubos, microplaca
│   ├── estatistica.py # média, desvio, variância, teste t, ANOVA
│   ├── tabelas.py     # organização em DataFrame + exportação CSV
│   └── exceptions.py  # erros de domínio
├── database/          # acesso a dados (SQLAlchemy)
│   ├── connection.py  # engine + sessão (agnóstico de motor)
│   ├── models.py      # tabelas (ORM)
│   ├── repositories.py# operações de banco (SQL isolado aqui)
│   └── seed.py        # dados de exemplo
├── services/          # orquestra core + database (ponto de entrada da UI/API)
│   ├── planejamento_service.py  # plano operacional
│   ├── experimento_service.py   # registro dos dados da bancada
│   └── estatistica_service.py   # análise + exportação
└── api/               # API HTTP opcional (FastAPI)
```

Fluxo de dependências (só para baixo): `ui/api → services → core / database`.

## 1. Instalar

```bash
cd Iniciacao-cientifica
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## 2. Ligar o banco

Por padrão usa SQLite (arquivo `planejador.db`, criado sozinho). Um comando:

```bash
python -m planejador.bootstrap
```

Isso cria as tabelas e insere dados de exemplo (reagentes, materiais e dois
protocolos). Idempotente — pode rodar quantas vezes quiser.

## 3. Usar o backend (fluxo completo)

Os quatro passos abaixo são o fluxo do aplicativo de ponta a ponta: escolher o
protocolo, gerar o plano, registrar o que voltou da bancada e analisar.

```python
from planejador.bootstrap import iniciar
from planejador.database import get_session
from planejador.services import (
    listar_protocolos, gerar_plano,
    criar_experimento, analisar_experimento, exportar_experimento_csv,
)

iniciar()  # garante banco pronto

with get_session() as sessao:
    # 1. selecionar o protocolo
    protocolo = listar_protocolos(sessao)[0]

    # 2. gerar o plano operacional (variáveis experimentais do usuário)
    plano = gerar_plano(
        sessao, protocolo["id"],
        n_amostras=8, n_replicatas=3, n_controles=2,
        excesso_percentual=10.0,
        conc_inicial=10.0, conc_final=1.0, volume_por_reacao=0.2,
    )
    for passo in plano.procedimento:
        print("-", passo)

    # 3. registrar os dados obtidos na bancada
    exp = criar_experimento(
        sessao, protocolo["id"], titulo="Ensaio 12/08",
        medicoes={"controle": [1.0, 1.1, 0.9], "tratamento": [5.0, 5.2, 4.8]},
    )

    # 4. analisar e disponibilizar
    print(analisar_experimento(sessao, exp["id"]))
    print(exportar_experimento_csv(sessao, exp["id"], "resultados/"))
```

O plano traz `reagentes`, `materiais`, `preparo` (diluição ou massa a pesar),
`tubos`, `microplaca` e `procedimento` — o resumo passo a passo, gerado a partir
dos próprios números calculados.

## 4. Ligar um frontend (PyQt6)

A UI deve chamar os **services** diretamente (não precisa de API):

```python
from planejador.services import gerar_plano   # dentro do app/ui
```

Os services devolvem dataclasses/dicts simples — fáceis de jogar numa tabela Qt.
As chaves `medicoes` e `resumo` de um experimento já vêm no formato
`list[dict]`, uma linha por registro, prontas para um `QTableWidget`.

## 5. Ligar via API (opcional, para frontend web/externo)

```bash
pip install -e ".[api]"
uvicorn planejador.api.app:app --reload
# Docs interativas em http://127.0.0.1:8000/docs
```

| Método | Rota | O que faz |
|---|---|---|
| `GET` | `/protocolos` | Lista os protocolos para seleção |
| `POST` | `/planos` | Gera o plano operacional |
| `POST` | `/experimentos` | Cria experimento (medições opcionais) |
| `GET` | `/experimentos` | Lista experimentos (filtro `protocolo_id`) |
| `GET` | `/experimentos/{id}` | Experimento com as medições tabuladas |
| `POST` | `/experimentos/{id}/medicoes` | Lança medições da bancada |
| `GET` | `/experimentos/{id}/estatistica` | Análise estatística (query `alpha`) |
| `POST` | `/experimentos/{id}/exportacoes` | Gera os CSV de medições e resumo |

Erros de domínio viram `404` (registro inexistente) ou `400` com
`{"mensagem": ..., "dica": ...}` — a dica é a sugestão de correção que a
interface pode exibir ao lado do campo errado.

## 6. Trocar de banco (SQLite → Postgres/MySQL)

Só muda a variável de ambiente — nenhuma linha de código:

```bash
# PostgreSQL
export APP_DATABASE_URL="postgresql+psycopg://user:senha@localhost:5432/planejador"
pip install -e ".[postgres]"

# MySQL
export APP_DATABASE_URL="mysql+pymysql://user:senha@localhost:3306/planejador"
pip install -e ".[mysql]"
```

## 7. Qualidade e testes

```bash
make test         # testes (cálculos, estatística, repositórios, services)
make lint         # ruff check
make format       # ruff format + fix
make type-check   # mypy
```

Ou diretamente: `pytest`, `ruff check backend tests`, `mypy backend`.

Os testes usam SQLite em memória — não tocam no banco real.

## 8. Problemas conhecidos

### `ModuleNotFoundError: No module named 'planejador'` depois de instalar

Acontece no macOS. O `pip install -e` grava um arquivo `.pth` em
`site-packages` apontando para `backend/`, mas o sistema pode marcar esse
arquivo com a flag `UF_HIDDEN` — e o módulo `site` do Python 3.11+ **ignora
arquivos `.pth` ocultos**. O pacote some do `sys.path` e todo import falha,
mesmo com o pacote instalado.

Para confirmar:

```bash
ls -lO .venv/lib/python3.12/site-packages/__editable__*.pth   # mostra "hidden"
```

O projeto já contorna isso: o `pyproject.toml` define
`pythonpath = ["backend"]` para o pytest, e o `Makefile` exporta
`PYTHONPATH=backend`. Por isso `make test` e `make db` funcionam
independentemente da flag.

Se precisar rodar algo fora do Makefile, use:

```bash
PYTHONPATH=backend python -m planejador.bootstrap
```

Limpar a flag manualmente (`chflags nohidden ...`) funciona, mas o sistema
costuma reaplicá-la — por isso a solução ficou na configuração do projeto.
