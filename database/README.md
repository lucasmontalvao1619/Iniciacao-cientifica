# database

Modelagem do banco (linguagem SQL).

- `schema.sql`: DDL de referência das tabelas (protocolos, reagentes, materiais,
  vínculos, experimentos, medições).
- `seed.sql`: reservado para dados iniciais em SQL.

Em execução, as tabelas são criadas automaticamente pelo SQLAlchemy
(`planejador.database.init_db`, via `python -m planejador.bootstrap`) a partir
dos modelos em `backend/planejador/database/models.py`. O `schema.sql` serve
como referência para revisão e para o MySQL Workbench, caso se opte por MySQL.

Banco atual: SQLite (padrão), agnóstico via SQLAlchemy. Ver `docs/decisoes/README.md`.
