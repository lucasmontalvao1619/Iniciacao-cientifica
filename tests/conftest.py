"""Fixtures compartilhadas dos testes.

Usa um banco SQLite em memória, isolado por teste, sem tocar no banco real.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from planejador.database.connection import Base


@pytest.fixture
def session() -> Iterator[Session]:
    """Sessão sobre um SQLite em memória, com as tabelas criadas."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, future=True
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    sessao = factory()
    try:
        yield sessao
        sessao.commit()
    finally:
        sessao.close()
        Base.metadata.drop_all(engine)
