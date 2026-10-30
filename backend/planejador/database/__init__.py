"""Camada de acesso a dados (SQLAlchemy).

Expõe os pontos de entrada mais usados para facilitar a conexão:

    from planejador.database import init_db, get_session
"""

from .connection import Base, get_engine, get_session, init_db

__all__ = ["Base", "get_engine", "get_session", "init_db"]
