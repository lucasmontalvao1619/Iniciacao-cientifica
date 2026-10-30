# Banco de dados

Modelagem para armazenar protocolos, variáveis experimentais, reagentes,
materiais, experimentos e resultados de análises.

## Motor

SQLite por padrão, acessado via **SQLAlchemy**, de forma agnóstica ao motor.
Trocar para PostgreSQL ou MySQL exige apenas alterar a variável de ambiente
`APP_DATABASE_URL` — o código de acesso não muda. Justificativa da escolha em
[decisões](../decisoes/README.md).

## Modelo de dados

```
protocolos 1---N protocolo_reagente N---1 reagentes
protocolos 1---N protocolo_material N---1 materiais
protocolos 1---N experimentos      1---N medicoes
```

- **protocolos**: nome, tipo (`preparo_solucao`, `diluicao`, `microplaca`...), descrição.
- **reagentes**: nome, unidade (g, mL, µL, M, %).
- **materiais**: nome, tipo (tubo, placa, ponteira...).
- **protocolo_reagente / protocolo_material**: vínculo N:N com `quantidade_base`
  por reação (usada no escalonamento).
- **experimentos**: execução de um protocolo (título, observações, data).
- **medicoes**: valores medidos por `grupo` (alimentam teste t / ANOVA).

## Estado atual

Implementado. As sete tabelas acima existem como modelos ORM, com chaves
primárias e estrangeiras definidas, e o banco é criado automaticamente na
primeira execução.

Quantidades usam `NUMERIC`/`DECIMAL` em vez de ponto flutuante, para evitar erro
de arredondamento em massas e volumes de reagentes.

Dados iniciais (reagentes, materiais e dois protocolos de exemplo) são semeados
por `backend/planejador/database/seed.py`, apenas quando o banco está vazio.

## Onde fica cada coisa

| Arquivo | Papel |
|---|---|
| `backend/planejador/database/models.py` | Modelos ORM — **fonte de verdade em runtime** |
| `backend/planejador/database/repositories.py` | Operações de leitura/escrita; todo o SQL fica isolado aqui |
| `backend/planejador/database/connection.py` | Engine e sessão, agnósticos de motor |
| `backend/planejador/database/seed.py` | Dados de exemplo |
| `database/schema.sql` | DDL de referência, para revisão e para o MySQL Workbench |
| `database/seed.sql` | Carga inicial em SQL puro, equivalente ao `seed.py` |

Em execução, as tabelas são criadas por `planejador.database.init_db()` a partir
dos modelos ORM. O `schema.sql` não é executado pela aplicação — serve de
documentação do modelo e de ponto de partida caso se migre para MySQL/Postgres.

## Segurança

Todo acesso passa pelos repositórios, que usam o ORM com parâmetros vinculados —
sem concatenação de strings, o que elimina a superfície de SQL injection.
Credenciais (quando houver servidor) vêm de variáveis de ambiente, nunca do
código. Ver `.env.example`.
