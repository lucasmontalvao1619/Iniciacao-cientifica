"""Ponto único para "ligar o banco" e deixar o backend pronto para uso.

Facilita a integração: o frontend (PyQt6) ou a API só precisam chamar
:func:`iniciar` uma vez ao subir a aplicação.

    from planejador.bootstrap import iniciar
    iniciar()  # cria as tabelas e popula dados de exemplo
"""

from __future__ import annotations

from .database import get_session, init_db
from .database.seed import semear


def iniciar(com_dados_exemplo: bool = True) -> None:
    """Cria as tabelas e, opcionalmente, popula dados de exemplo.

    Idempotente: pode ser chamada toda vez que o app inicia.

    Args:
        com_dados_exemplo: Se ``True``, semeia reagentes/materiais/protocolos
            de exemplo (só quando o banco está vazio).
    """
    init_db()
    if com_dados_exemplo:
        with get_session() as session:
            semear(session)


if __name__ == "__main__":
    iniciar()
    print("Banco iniciado com sucesso (tabelas criadas e dados de exemplo).")
