"""Serviço de estatística: aplica as análises do núcleo a dados do usuário.

Aceita tanto dados em memória (dict de grupos) quanto dados persistidos
(medições de um experimento), devolvendo um relatório serializável.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from sqlalchemy.orm import Session

from ..core import estatistica, tabelas
from ..core.exceptions import EntradaInvalida
from ..database import repositories


def analisar_grupos(
    grupos: Mapping[str, Sequence[float]], *, alpha: float = 0.05
) -> dict:
    """Analisa grupos de valores e devolve um relatório estatístico.

    Para cada grupo calcula o resumo descritivo. Se houver exatamente 2 grupos,
    roda teste t; se houver 3 ou mais, roda ANOVA de uma via.

    Args:
        grupos: Mapa ``{nome_do_grupo: [valores...]}``.
        alpha: Nível de significância.

    Returns:
        Dicionário com ``resumos`` por grupo, as tabelas estruturadas
        (``tabela_medicoes`` e ``tabela_resumo``) e, quando aplicável,
        ``teste_t`` ou ``anova``.

    Raises:
        EntradaInvalida: Se não houver nenhum grupo.
    """
    if not grupos:
        raise EntradaInvalida("Nenhum grupo de dados foi fornecido.")

    resumos = {
        nome: vars(estatistica.resumo(valores))
        for nome, valores in grupos.items()
    }
    relatorio: dict = {
        "resumos": resumos,
        "tabela_medicoes": tabelas.para_registros(
            tabelas.tabela_medicoes(grupos)
        ),
        "tabela_resumo": tabelas.para_registros(tabelas.tabela_resumo(grupos)),
        "teste_t": None,
        "anova": None,
    }

    nomes = list(grupos.keys())
    if len(nomes) == 2:
        resultado = estatistica.teste_t(
            grupos[nomes[0]], grupos[nomes[1]], alpha=alpha
        )
        relatorio["teste_t"] = {"grupos": nomes, **vars(resultado)}
    elif len(nomes) >= 3:
        resultado_anova = estatistica.anova_uma_via(
            *grupos.values(), alpha=alpha
        )
        relatorio["anova"] = {"grupos": nomes, **vars(resultado_anova)}

    return relatorio


def analisar_experimento(
    session: Session, experimento_id: int, *, alpha: float = 0.05
) -> dict:
    """Carrega as medições de um experimento e as analisa.

    Args:
        session: Sessão do banco.
        experimento_id: Experimento a analisar.
        alpha: Nível de significância.

    Returns:
        Mesmo formato de :func:`analisar_grupos`.

    Raises:
        EntradaInvalida: Se o experimento não tiver medições.
    """
    grupos = repositories.medicoes_por_grupo(session, experimento_id)
    if not grupos:
        raise EntradaInvalida(
            f"O experimento id={experimento_id} não possui medições registradas.",
            dica="Registre as medições do experimento antes de analisá-lo.",
        )
    return analisar_grupos(grupos, alpha=alpha)


def exportar_experimento_csv(
    session: Session, experimento_id: int, destino: str | Path
) -> dict[str, str]:
    """Exporta as tabelas de um experimento para dois arquivos CSV.

    Fecha a etapa "exibe e disponibiliza os resultados": gera
    ``<destino>/experimento_<id>_medicoes.csv`` com os dados brutos e
    ``..._resumo.csv`` com as estatísticas por grupo, em formato que o Excel em
    português abre já colunado.

    Args:
        session: Sessão do banco.
        experimento_id: Experimento a exportar.
        destino: Diretório de saída (criado se não existir).

    Returns:
        Mapa ``{"medicoes": caminho, "resumo": caminho}``.

    Raises:
        EntradaInvalida: Se o experimento não tiver medições.
    """
    grupos = repositories.medicoes_por_grupo(session, experimento_id)
    if not grupos:
        raise EntradaInvalida(
            f"O experimento id={experimento_id} não possui medições registradas."
        )
    pasta = Path(destino)
    prefixo = f"experimento_{experimento_id}"
    caminho_medicoes = tabelas.exportar_csv(
        tabelas.tabela_medicoes(grupos), pasta / f"{prefixo}_medicoes.csv"
    )
    caminho_resumo = tabelas.exportar_csv(
        tabelas.tabela_resumo(grupos), pasta / f"{prefixo}_resumo.csv"
    )
    return {
        "medicoes": str(caminho_medicoes),
        "resumo": str(caminho_resumo),
    }
