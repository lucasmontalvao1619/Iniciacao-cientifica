"""Modelos ORM (tabelas) do domínio experimental.

Estrutura mínima da versão inicial (microbiologia):

    Protocolo 1---N ProtocoloReagente N---1 Reagente
    Protocolo 1---N ProtocoloMaterial N---1 Material
    Protocolo 1---N Experimento 1---N Medicao

Valores numéricos usam ``Numeric`` (decimal) para evitar erro de arredondamento
em quantidades de reagentes.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .connection import Base


class Protocolo(Base):
    """Protocolo laboratorial (ex.: preparo de solução, diluição seriada)."""

    __tablename__ = "protocolos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    tipo: Mapped[str] = mapped_column(String(60), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)

    reagentes: Mapped[list[ProtocoloReagente]] = relationship(
        back_populates="protocolo", cascade="all, delete-orphan"
    )
    materiais: Mapped[list[ProtocoloMaterial]] = relationship(
        back_populates="protocolo", cascade="all, delete-orphan"
    )
    experimentos: Mapped[list[Experimento]] = relationship(
        back_populates="protocolo", cascade="all, delete-orphan"
    )


class Reagente(Base):
    """Reagente utilizável em protocolos."""

    __tablename__ = "reagentes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False)


class Material(Base):
    """Material ou vidraria (ex.: tubo, placa, ponteira)."""

    __tablename__ = "materiais"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    tipo: Mapped[str | None] = mapped_column(String(60))


class ProtocoloReagente(Base):
    """Reagente exigido por um protocolo, com quantidade base por reação."""

    __tablename__ = "protocolo_reagente"

    id: Mapped[int] = mapped_column(primary_key=True)
    protocolo_id: Mapped[int] = mapped_column(
        ForeignKey("protocolos.id"), nullable=False
    )
    reagente_id: Mapped[int] = mapped_column(
        ForeignKey("reagentes.id"), nullable=False
    )
    quantidade_base: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    protocolo: Mapped[Protocolo] = relationship(back_populates="reagentes")
    reagente: Mapped[Reagente] = relationship()


class ProtocoloMaterial(Base):
    """Material exigido por um protocolo, com quantidade base por reação."""

    __tablename__ = "protocolo_material"

    id: Mapped[int] = mapped_column(primary_key=True)
    protocolo_id: Mapped[int] = mapped_column(
        ForeignKey("protocolos.id"), nullable=False
    )
    material_id: Mapped[int] = mapped_column(
        ForeignKey("materiais.id"), nullable=False
    )
    quantidade_base: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    protocolo: Mapped[Protocolo] = relationship(back_populates="materiais")
    material: Mapped[Material] = relationship()


class Experimento(Base):
    """Registro de um experimento executado a partir de um protocolo."""

    __tablename__ = "experimentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    protocolo_id: Mapped[int] = mapped_column(
        ForeignKey("protocolos.id"), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(160), nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    protocolo: Mapped[Protocolo] = relationship(back_populates="experimentos")
    medicoes: Mapped[list[Medicao]] = relationship(
        back_populates="experimento", cascade="all, delete-orphan"
    )


class Medicao(Base):
    """Valor medido em um experimento, associado a um grupo (para estatística)."""

    __tablename__ = "medicoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    experimento_id: Mapped[int] = mapped_column(
        ForeignKey("experimentos.id"), nullable=False
    )
    grupo: Mapped[str] = mapped_column(String(60), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(14, 6), nullable=False)

    experimento: Mapped[Experimento] = relationship(back_populates="medicoes")
