"""Histórico local de dez planejamentos; itens retirados viram arquivos de consulta."""

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import Column, MetaData, String, Table, Text, create_engine, select
from sqlalchemy.engine import URL, Connection
from sqlalchemy.exc import OperationalError


class Historico:
    def __init__(self, directory: Path, archive_directory: Path | None = None) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.archive_dir = (
            archive_directory or self.directory / "Registros de Experimentos"
        )
        try:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            self.archive_dir = self.directory / "Registros de Experimentos"
            self.archive_dir.mkdir(exist_ok=True)
        self.engine = create_engine(
            URL.create("sqlite", database=str(self.directory / "historico.sqlite3"))
        )
        metadata = MetaData()
        self.table = Table(
            "historico",
            metadata,
            Column("id", String, primary_key=True),
            Column("atualizado_em", String, nullable=False),
            Column("conteudo", Text, nullable=False),
        )
        metadata.create_all(self.engine)

    def list(self) -> list[dict]:
        with self.engine.connect() as conn:
            return [
                dict(row._mapping)
                for row in conn.execute(
                    select(self.table)
                    .order_by(self.table.c.atualizado_em.desc(), self.table.c.id.desc())
                    .limit(10)
                )
            ]

    def save(self, payload: dict, record_id: str | None = None) -> str:
        record_id = record_id or uuid4().hex
        try:
            return self._save(payload, record_id)
        except OperationalError as exc:
            if (
                getattr(exc.orig, "sqlite_errorcode", None)
                != sqlite3.SQLITE_READONLY_DBMOVED
            ):
                raise
            # SQLite mantém o caminho resolvido na conexão após mover a pasta.
            self.engine.dispose()
            return self._save(payload, record_id)

    def _save(self, payload: dict, record_id: str) -> str:
        now = datetime.now(UTC).isoformat()
        content = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        with self.engine.begin() as conn:
            exists = conn.execute(
                select(self.table.c.id).where(self.table.c.id == record_id)
            ).first()
            if exists:
                conn.execute(
                    self.table.update()
                    .where(self.table.c.id == record_id)
                    .values(atualizado_em=now, conteudo=content)
                )
            else:
                conn.execute(
                    self.table.insert().values(
                        id=record_id, atualizado_em=now, conteudo=content
                    )
                )
            overflow = conn.execute(
                select(self.table)
                .order_by(self.table.c.atualizado_em.desc(), self.table.c.id.desc())
                .offset(10)
            ).fetchall()
            for row in overflow:
                self._archive(conn, dict(row._mapping))
        return record_id

    def _archive(self, conn: Connection, record: dict) -> Path:
        # Write first: a failed archive must leave the database record intact.
        target = self.archive_dir / f"{record['id']}-{uuid4().hex[:8]}.json"
        temp = target.with_suffix(".tmp")
        try:
            temp.write_text(
                json.dumps(
                    {
                        "id": record["id"],
                        "atualizado_em": record["atualizado_em"],
                        "consulta_apenas": True,
                        "experimento": json.loads(record["conteudo"]),
                    },
                    ensure_ascii=False,
                    indent=2,
                    allow_nan=False,
                ),
                encoding="utf-8",
            )
            temp.replace(target)
        finally:
            temp.unlink(missing_ok=True)
        conn.execute(self.table.delete().where(self.table.c.id == record["id"]))
        return target

    def archive(self, record_id: str) -> Path:
        with self.engine.begin() as conn:
            row = conn.execute(
                select(self.table).where(self.table.c.id == record_id)
            ).first()
            if row is None:
                raise ValueError("Experimento não encontrado no histórico.")
            return self._archive(conn, dict(row._mapping))
