"""Exceções de domínio do planejamento experimental.

A UI e a API capturam :class:`ErroPlanejamento` para exibir mensagens claras
ao usuário sem quebrar a aplicação.
"""

from __future__ import annotations


class ErroPlanejamento(Exception):
    """Exceção base do domínio."""


class EntradaInvalida(ErroPlanejamento):
    """Entrada do usuário inválida (ex.: volume negativo, unidade ausente).

    Attributes:
        dica: Sugestão opcional de correção, exibível na interface.
    """

    def __init__(self, mensagem: str, *, dica: str | None = None) -> None:
        super().__init__(mensagem)
        self.dica = dica


class RegistroNaoEncontrado(ErroPlanejamento):
    """Registro solicitado não existe no banco (ex.: protocolo inexistente)."""
