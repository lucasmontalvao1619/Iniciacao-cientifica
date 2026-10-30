"""Serviço de experimentos: registra o que voltou da bancada.

Fecha a etapa "insere os dados experimentais obtidos" do fluxo do aplicativo.
Depois de executar o protocolo, o usuário cria o experimento e lança as
medições agrupadas (controle, tratamento, ...); daí em diante os dados já
saem daqui organizados em tabela, prontos para a análise estatística.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from sqlalchemy.orm import Session

from ..core.exceptions import EntradaInvalida
from ..database import repositories


def _validar_medicoes(medicoes: Mapping[str, Sequence[float]]) -> None:
    """Rejeita lotes vazios ou com grupos sem nenhum valor."""
    if not medicoes:
        raise EntradaInvalida(
            "Nenhuma medição foi informada.",
            dica="Envie ao menos um grupo, ex.: {'controle': [1.0, 1.2]}.",
        )
    vazios = [nome for nome, valores in medicoes.items() if len(valores) == 0]
    if vazios:
        raise EntradaInvalida(
            f"Grupo(s) sem nenhuma medição: {', '.join(sorted(vazios))}.",
            dica="Remova o grupo ou insira ao menos um valor medido.",
        )


def criar_experimento(
    session: Session,
    protocolo_id: int,
    titulo: str,
    *,
    observacoes: str | None = None,
    medicoes: Mapping[str, Sequence[float]] | None = None,
) -> dict:
    """Cria um experimento e, opcionalmente, já registra suas medições.

    Args:
        session: Sessão do banco.
        protocolo_id: Protocolo executado.
        titulo: Identificação do experimento (ex.: "Ensaio 12/08").
        observacoes: Anotações livres de bancada.
        medicoes: Mapa ``{grupo: [valores...]}`` a registrar de imediato.

    Returns:
        Dicionário do experimento, no formato de :func:`obter_experimento`.

    Raises:
        RegistroNaoEncontrado: Se o protocolo não existir.
        EntradaInvalida: Se o título for vazio ou as medições forem inválidas.
    """
    if not titulo.strip():
        raise EntradaInvalida("O título do experimento não pode ser vazio.")

    experimento = repositories.criar_experimento(
        session, protocolo_id, titulo.strip(), observacoes
    )
    if medicoes:
        _validar_medicoes(medicoes)
        repositories.registrar_medicoes(session, experimento.id, medicoes)
    return obter_experimento(session, experimento.id)


def adicionar_medicoes(
    session: Session,
    experimento_id: int,
    medicoes: Mapping[str, Sequence[float]],
) -> dict:
    """Acrescenta medições a um experimento existente.

    Valores de um grupo já existente são acumulados, não substituídos — é o
    comportamento esperado quando as leituras chegam em tandas.

    Args:
        session: Sessão do banco.
        experimento_id: Experimento de destino.
        medicoes: Mapa ``{grupo: [valores...]}``.

    Returns:
        Dicionário do experimento atualizado.

    Raises:
        RegistroNaoEncontrado: Se o experimento não existir.
        EntradaInvalida: Se o lote de medições for inválido.
    """
    _validar_medicoes(medicoes)
    repositories.registrar_medicoes(session, experimento_id, medicoes)
    return obter_experimento(session, experimento_id)


def obter_experimento(session: Session, experimento_id: int) -> dict:
    """Devolve um experimento com suas medições já tabuladas.

    Args:
        session: Sessão do banco.
        experimento_id: Experimento a carregar.

    Returns:
        Dicionário com metadados, ``grupos`` (mapa bruto) e as tabelas
        ``medicoes`` (formato longo) e ``resumo`` (descritivas por grupo).
        As tabelas vêm vazias enquanto não houver medições.

    Raises:
        RegistroNaoEncontrado: Se o experimento não existir.
    """
    from ..core import tabelas

    experimento = repositories.obter_experimento(session, experimento_id)
    grupos = repositories.medicoes_por_grupo(session, experimento_id)

    base: dict = {
        "id": experimento.id,
        "protocolo_id": experimento.protocolo_id,
        "protocolo": experimento.protocolo.nome,
        "titulo": experimento.titulo,
        "observacoes": experimento.observacoes,
        "criado_em": (
            experimento.criado_em.isoformat() if experimento.criado_em else None
        ),
        "grupos": grupos,
        "n_medicoes": sum(len(v) for v in grupos.values()),
    }
    if not grupos:
        return {**base, "medicoes": [], "resumo": []}
    return {
        **base,
        "medicoes": tabelas.para_registros(tabelas.tabela_medicoes(grupos)),
        "resumo": tabelas.para_registros(tabelas.tabela_resumo(grupos)),
    }


def listar_experimentos(
    session: Session, protocolo_id: int | None = None
) -> list[dict]:
    """Lista experimentos (do mais recente ao mais antigo), sem as tabelas.

    Args:
        session: Sessão do banco.
        protocolo_id: Se informado, restringe ao protocolo indicado.

    Returns:
        Lista de dicionários resumidos, para preencher a tela de seleção.
    """
    return [
        {
            "id": e.id,
            "protocolo_id": e.protocolo_id,
            "protocolo": e.protocolo.nome,
            "titulo": e.titulo,
            "criado_em": e.criado_em.isoformat() if e.criado_em else None,
        }
        for e in repositories.listar_experimentos(session, protocolo_id)
    ]


def listar_protocolos(session: Session) -> list[dict]:
    """Lista os protocolos disponíveis para seleção.

    Primeira etapa do fluxo do aplicativo — o usuário escolhe daqui antes de
    informar as variáveis experimentais.

    Returns:
        Lista de dicionários com ``id``, ``nome``, ``tipo`` e ``descricao``.
    """
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "tipo": p.tipo,
            "descricao": p.descricao,
        }
        for p in repositories.listar_protocolos(session)
    ]
