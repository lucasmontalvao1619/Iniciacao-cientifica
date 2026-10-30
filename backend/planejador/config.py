"""Configuração central do backend.

Todas as opções vêm de variáveis de ambiente, com padrões seguros para
execução local. Nenhuma credencial fica no código.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Configurações imutáveis da aplicação.

    Attributes:
        database_url: URL de conexão no formato SQLAlchemy.
        db_echo: Se ``True``, imprime o SQL gerado (útil para depurar).
    """

    database_url: str
    db_echo: bool


def get_settings() -> Settings:
    """Lê as configurações do ambiente.

    Returns:
        Instância de :class:`Settings` já resolvida.

    Example:
        >>> s = get_settings()
        >>> s.database_url.startswith("sqlite")
        True
    """
    url = os.environ.get("APP_DATABASE_URL", "sqlite:///planejador.db")
    echo = os.environ.get("APP_DB_ECHO", "false").strip().lower() == "true"
    return Settings(database_url=url, db_echo=echo)
