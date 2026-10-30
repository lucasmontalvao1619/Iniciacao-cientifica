"""Dados iniciais de exemplo (reagentes, materiais e um protocolo microbiológico).

Serve para o app funcionar já com conteúdo demonstrável. É idempotente: se já
houver protocolos, não duplica nada.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Protocolo
from .repositories import (
    criar_material,
    criar_protocolo,
    criar_reagente,
    vincular_material,
    vincular_reagente,
)


def semear(session: Session) -> None:
    """Popula o banco com dados de exemplo, se ainda estiver vazio."""
    ja_tem = session.scalar(select(Protocolo).limit(1))
    if ja_tem is not None:
        return

    # Reagentes
    nacl = criar_reagente(session, "Cloreto de sódio (NaCl)", "g")
    agua = criar_reagente(session, "Água destilada", "mL")
    caldo = criar_reagente(session, "Caldo nutriente", "g")

    # Materiais
    tubo = criar_material(session, "Tubo de ensaio", "tubo")
    placa = criar_material(session, "Microplaca 96 poços", "placa")
    ponteira = criar_material(session, "Ponteira 200 µL", "ponteira")

    # Protocolo de exemplo: preparo de solução salina 0,9%
    salina = criar_protocolo(
        session,
        nome="Preparo de solução salina 0,9%",
        tipo="preparo_solucao",
        descricao="Solução salina fisiológica para diluições microbiológicas.",
    )
    vincular_reagente(session, salina.id, nacl.id, quantidade_base=0.9)
    vincular_reagente(session, salina.id, agua.id, quantidade_base=100.0)
    vincular_material(session, salina.id, tubo.id, quantidade_base=1.0)

    # Protocolo de exemplo: ensaio em microplaca
    microplaca = criar_protocolo(
        session,
        nome="Ensaio de crescimento em microplaca",
        tipo="microplaca",
        descricao="Ensaio de crescimento microbiano com leitura em microplaca.",
    )
    vincular_reagente(session, microplaca.id, caldo.id, quantidade_base=0.2)
    vincular_material(session, microplaca.id, placa.id, quantidade_base=1.0)
    vincular_material(session, microplaca.id, ponteira.id, quantidade_base=1.0)
