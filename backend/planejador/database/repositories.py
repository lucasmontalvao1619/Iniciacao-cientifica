"""Repositórios: isolam o acesso ao banco do restante da aplicação.

Cada função recebe uma :class:`~sqlalchemy.orm.Session` e opera sobre os modelos.
Nenhum SQL cru é escrito à mão — o ORM cuida da parametrização, evitando SQL
injection. Services e API sempre passam por aqui, nunca acessam o banco direto.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.exceptions import RegistroNaoEncontrado
from .models import (
    Experimento,
    Material,
    Medicao,
    Protocolo,
    ProtocoloMaterial,
    ProtocoloReagente,
    Reagente,
)

# --------------------------------------------------------------------------- #
# Reagentes / Materiais
# --------------------------------------------------------------------------- #


def criar_reagente(session: Session, nome: str, unidade: str) -> Reagente:
    """Cria e persiste um reagente."""
    reagente = Reagente(nome=nome, unidade=unidade)
    session.add(reagente)
    session.flush()
    return reagente


def listar_reagentes(session: Session) -> Sequence[Reagente]:
    """Lista todos os reagentes, ordenados por nome."""
    return session.scalars(select(Reagente).order_by(Reagente.nome)).all()


def criar_material(
    session: Session, nome: str, tipo: str | None = None
) -> Material:
    """Cria e persiste um material."""
    material = Material(nome=nome, tipo=tipo)
    session.add(material)
    session.flush()
    return material


def listar_materiais(session: Session) -> Sequence[Material]:
    """Lista todos os materiais, ordenados por nome."""
    return session.scalars(select(Material).order_by(Material.nome)).all()


# --------------------------------------------------------------------------- #
# Protocolos
# --------------------------------------------------------------------------- #


def criar_protocolo(
    session: Session, nome: str, tipo: str, descricao: str | None = None
) -> Protocolo:
    """Cria e persiste um protocolo."""
    protocolo = Protocolo(nome=nome, tipo=tipo, descricao=descricao)
    session.add(protocolo)
    session.flush()
    return protocolo


def obter_protocolo(session: Session, protocolo_id: int) -> Protocolo:
    """Busca um protocolo por id.

    Raises:
        RegistroNaoEncontrado: Se o protocolo não existir.
    """
    protocolo = session.get(Protocolo, protocolo_id)
    if protocolo is None:
        raise RegistroNaoEncontrado(
            f"Protocolo com id={protocolo_id} não encontrado."
        )
    return protocolo


def listar_protocolos(session: Session) -> Sequence[Protocolo]:
    """Lista todos os protocolos, ordenados por nome."""
    return session.scalars(select(Protocolo).order_by(Protocolo.nome)).all()


def vincular_reagente(
    session: Session,
    protocolo_id: int,
    reagente_id: int,
    quantidade_base: float,
) -> ProtocoloReagente:
    """Associa um reagente a um protocolo com a quantidade base por reação."""
    vinculo = ProtocoloReagente(
        protocolo_id=protocolo_id,
        reagente_id=reagente_id,
        quantidade_base=quantidade_base,
    )
    session.add(vinculo)
    session.flush()
    return vinculo


def vincular_material(
    session: Session,
    protocolo_id: int,
    material_id: int,
    quantidade_base: float,
) -> ProtocoloMaterial:
    """Associa um material a um protocolo com a quantidade base por reação."""
    vinculo = ProtocoloMaterial(
        protocolo_id=protocolo_id,
        material_id=material_id,
        quantidade_base=quantidade_base,
    )
    session.add(vinculo)
    session.flush()
    return vinculo


# --------------------------------------------------------------------------- #
# Experimentos / Medições
# --------------------------------------------------------------------------- #


def criar_experimento(
    session: Session,
    protocolo_id: int,
    titulo: str,
    observacoes: str | None = None,
) -> Experimento:
    """Cria e persiste um experimento vinculado a um protocolo."""
    # valida existência do protocolo (levanta RegistroNaoEncontrado se ausente)
    obter_protocolo(session, protocolo_id)
    experimento = Experimento(
        protocolo_id=protocolo_id, titulo=titulo, observacoes=observacoes
    )
    session.add(experimento)
    session.flush()
    return experimento


def obter_experimento(session: Session, experimento_id: int) -> Experimento:
    """Busca um experimento por id.

    Raises:
        RegistroNaoEncontrado: Se o experimento não existir.
    """
    experimento = session.get(Experimento, experimento_id)
    if experimento is None:
        raise RegistroNaoEncontrado(
            f"Experimento com id={experimento_id} não encontrado."
        )
    return experimento


def listar_experimentos(
    session: Session, protocolo_id: int | None = None
) -> Sequence[Experimento]:
    """Lista experimentos, do mais recente para o mais antigo.

    Args:
        session: Sessão do banco.
        protocolo_id: Se informado, restringe ao protocolo indicado.
    """
    stmt = select(Experimento)
    if protocolo_id is not None:
        stmt = stmt.where(Experimento.protocolo_id == protocolo_id)
    stmt = stmt.order_by(Experimento.id.desc())
    return session.scalars(stmt).all()


def registrar_medicao(
    session: Session, experimento_id: int, grupo: str, valor: float
) -> Medicao:
    """Registra um valor medido em um experimento, associado a um grupo."""
    medicao = Medicao(experimento_id=experimento_id, grupo=grupo, valor=valor)
    session.add(medicao)
    session.flush()
    return medicao


def registrar_medicoes(
    session: Session,
    experimento_id: int,
    grupos: Mapping[str, Sequence[float]],
) -> list[Medicao]:
    """Registra vários valores de uma vez, agrupados por nome de grupo.

    Uma única ida ao banco para o lote inteiro — é o caminho usado quando o
    usuário digita a planilha de resultados da bancada.

    Args:
        session: Sessão do banco.
        experimento_id: Experimento de destino.
        grupos: Mapa ``{nome_do_grupo: [valores...]}``.

    Returns:
        As medições criadas.

    Raises:
        RegistroNaoEncontrado: Se o experimento não existir.
    """
    obter_experimento(session, experimento_id)
    medicoes = [
        Medicao(experimento_id=experimento_id, grupo=grupo, valor=float(valor))
        for grupo, valores in grupos.items()
        for valor in valores
    ]
    session.add_all(medicoes)
    session.flush()
    return medicoes


def medicoes_por_grupo(
    session: Session, experimento_id: int
) -> dict[str, list[float]]:
    """Devolve as medições de um experimento agrupadas por ``grupo``.

    Útil para alimentar as análises estatísticas (teste t, ANOVA).
    """
    stmt = select(Medicao).where(Medicao.experimento_id == experimento_id)
    grupos: dict[str, list[float]] = {}
    for medicao in session.scalars(stmt):
        grupos.setdefault(medicao.grupo, []).append(float(medicao.valor))
    return grupos
