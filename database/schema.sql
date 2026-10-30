-- Schema de referência (linguagem SQL) do Planejador de Experimentos.
--
-- Este arquivo documenta a modelagem. Em execução, as tabelas são criadas
-- automaticamente pelo SQLAlchemy (planejador.database.init_db) a partir dos
-- modelos em backend/planejador/database/models.py — este .sql serve como
-- referência para o MySQL Workbench / revisão do modelo.
--
-- Sintaxe compatível com SQLite; para Postgres/MySQL, ajuste os tipos
-- (INTEGER PRIMARY KEY AUTOINCREMENT -> SERIAL / AUTO_INCREMENT).

CREATE TABLE protocolos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        VARCHAR(120) NOT NULL UNIQUE,
    tipo        VARCHAR(60)  NOT NULL,
    descricao   TEXT
);

CREATE TABLE reagentes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        VARCHAR(120) NOT NULL UNIQUE,
    unidade     VARCHAR(20)  NOT NULL
);

CREATE TABLE materiais (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        VARCHAR(120) NOT NULL UNIQUE,
    tipo        VARCHAR(60)
);

CREATE TABLE protocolo_reagente (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    protocolo_id     INTEGER NOT NULL,
    reagente_id      INTEGER NOT NULL,
    quantidade_base  NUMERIC(12,4) NOT NULL,
    FOREIGN KEY (protocolo_id) REFERENCES protocolos(id),
    FOREIGN KEY (reagente_id)  REFERENCES reagentes(id)
);

CREATE TABLE protocolo_material (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    protocolo_id     INTEGER NOT NULL,
    material_id      INTEGER NOT NULL,
    quantidade_base  NUMERIC(12,4) NOT NULL,
    FOREIGN KEY (protocolo_id) REFERENCES protocolos(id),
    FOREIGN KEY (material_id)  REFERENCES materiais(id)
);

CREATE TABLE experimentos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    protocolo_id  INTEGER NOT NULL,
    titulo        VARCHAR(160) NOT NULL,
    observacoes   TEXT,
    criado_em     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (protocolo_id) REFERENCES protocolos(id)
);

CREATE TABLE medicoes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    experimento_id  INTEGER NOT NULL,
    grupo           VARCHAR(60) NOT NULL,
    valor           NUMERIC(14,6) NOT NULL,
    FOREIGN KEY (experimento_id) REFERENCES experimentos(id)
);
