"""Conexão e sessão do banco (agnóstico de motor via SQLAlchemy).

Toda a configuração vem de :func:`planejador.config.get_settings`, ou seja, da
variável de ambiente ``APP_DATABASE_URL``. Trocar SQLite por Postgres/MySQL é só
mudar essa URL — nada mais no código muda.

Uso típico:

    from planejador.database import init_db, get_session

    init_db()                     # cria as tabelas (idempotente)
    with get_session() as sessao: # abre/fecha e faz commit/rollback sozinho
        ...
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..config import get_settings


class Base(DeclarativeBase):
    """Base declarativa para todos os modelos ORM."""


# Engine e fábrica de sessões são criados sob demanda (lazy) e reutilizados.
_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Devolve o engine único da aplicação, criando-o na primeira chamada."""
    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        # check_same_thread=False permite usar a conexão SQLite fora da thread
        # que a criou (necessário quando a UI roda em thread separada).
        connect_args = (
            {"check_same_thread": False}
            if settings.database_url.startswith("sqlite")
            else {}
        )
        _engine = create_engine(
            settings.database_url,
            echo=settings.db_echo,
            future=True,
            connect_args=connect_args,
        )
        _session_factory = sessionmaker(
            bind=_engine, expire_on_commit=False, future=True
        )
    return _engine


def _get_session_factory() -> sessionmaker[Session]:
    """Garante que a fábrica de sessões esteja pronta."""
    if _session_factory is None:
        get_engine()
    assert _session_factory is not None  # noqa: S101 - garantido acima
    return _session_factory


def init_db() -> None:
    """Cria todas as tabelas mapeadas (idempotente).

    Importa os modelos para registrá-los na metadata antes de criar as tabelas.
    """
    from . import models  # noqa: F401 - registra os modelos na metadata

    Base.metadata.create_all(bind=get_engine())


@contextmanager
def get_session() -> Iterator[Session]:
    """Context manager de sessão com commit/rollback automáticos.

    Faz commit ao final se tudo correr bem, ou rollback em caso de exceção, e
    sempre fecha a sessão.

    Yields:
        Sessão do SQLAlchemy pronta para uso.
    """
    session = _get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
