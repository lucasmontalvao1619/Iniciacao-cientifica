"""Camada de serviços: orquestra core + database e expõe operações prontas.

É por aqui que o frontend (PyQt6) ou a API devem entrar. Os services recebem
tipos simples e devolvem dicionários/dataclasses, sem vazar detalhes do ORM.

O conjunto cobre o fluxo completo do aplicativo, na ordem em que o usuário o
percorre: escolher o protocolo (:func:`listar_protocolos`), gerar o plano
operacional (:func:`gerar_plano`), registrar o que voltou da bancada
(:func:`criar_experimento`, :func:`adicionar_medicoes`) e analisar os
resultados (:func:`analisar_experimento`, :func:`exportar_experimento_csv`).
"""

from typing import Any

from .experimento_service import (
    adicionar_medicoes,
    criar_experimento,
    listar_experimentos,
    listar_protocolos,
    obter_experimento,
)
from .planejamento_service import (
    ItemPlano,
    PlanoOperacional,
    PreparoSolucao,
    gerar_plano,
)

__all__ = [
    "ItemPlano",
    "PlanoOperacional",
    "PreparoSolucao",
    "gerar_plano",
    "listar_protocolos",
    "criar_experimento",
    "adicionar_medicoes",
    "obter_experimento",
    "listar_experimentos",
    "analisar_grupos",
    "analisar_experimento",
    "exportar_experimento_csv",
]


def __getattr__(name: str) -> Any:
    """Carrega estatística apenas quando um de seus serviços é solicitado."""
    if name not in {
        "analisar_experimento",
        "analisar_grupos",
        "exportar_experimento_csv",
    }:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from . import estatistica_service

    value = getattr(estatistica_service, name)
    globals()[name] = value
    return value
