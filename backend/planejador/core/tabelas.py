"""Organização de dados experimentais em tabelas estruturadas (Pandas).

Corresponde à etapa "organiza os dados em tabelas estruturadas" do fluxo do
aplicativo: os valores medidos chegam como listas soltas por grupo e saem daqui
como ``DataFrame`` — formato longo para os dados brutos, e uma tabela de resumo
por grupo pronta para exibição ou exportação.

Como o resto do ``core``, este módulo é puro: não acessa banco, não desenha
nada e não conhece a interface. A apresentação (tela, CSV, planilha) fica a
cargo das camadas superiores.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .exceptions import EntradaInvalida

# Colunas da tabela de resumo, na ordem em que aparecem.
COLUNAS_RESUMO = [
    "grupo",
    "n",
    "media",
    "desvio_padrao",
    "variancia",
    "erro_padrao",
    "cv_percentual",
    "minimo",
    "maximo",
]


def _validar_grupos(grupos: Mapping[str, Sequence[float]]) -> None:
    """Valida que há pelo menos um grupo e que nenhum está vazio."""
    if not grupos:
        raise EntradaInvalida(
            "Nenhum grupo de dados foi fornecido.",
            dica="Informe ao menos um grupo, ex.: {'controle': [1.0, 1.2]}.",
        )
    vazios = [nome for nome, valores in grupos.items() if len(valores) == 0]
    if vazios:
        raise EntradaInvalida(
            f"Grupo(s) sem nenhuma medição: {', '.join(sorted(vazios))}.",
            dica="Remova o grupo ou insira ao menos um valor medido.",
        )


def tabela_medicoes(grupos: Mapping[str, Sequence[float]]) -> pd.DataFrame:
    """Monta a tabela de dados brutos em formato longo.

    Args:
        grupos: Mapa ``{nome_do_grupo: [valores...]}``.

    Returns:
        ``DataFrame`` com as colunas ``grupo``, ``replicata`` (1-based) e
        ``valor``, ordenado por grupo e replicata.

    Raises:
        EntradaInvalida: Se não houver grupos ou algum grupo estiver vazio.

    Example:
        >>> df = tabela_medicoes({"controle": [1.0, 1.2]})
        >>> list(df.columns)
        ['grupo', 'replicata', 'valor']
    """
    _validar_grupos(grupos)
    linhas = [
        {"grupo": nome, "replicata": i, "valor": float(valor)}
        for nome, valores in grupos.items()
        for i, valor in enumerate(valores, start=1)
    ]
    return pd.DataFrame(linhas, columns=["grupo", "replicata", "valor"])


def tabela_resumo(grupos: Mapping[str, Sequence[float]]) -> pd.DataFrame:
    """Monta a tabela de estatísticas descritivas por grupo.

    Inclui o coeficiente de variação (CV%), muito usado em bancada para julgar
    a repetibilidade entre replicatas. Grupos com uma única medição não têm
    dispersão definida e recebem ``NaN`` nessas colunas, em vez de erro.

    Args:
        grupos: Mapa ``{nome_do_grupo: [valores...]}``.

    Returns:
        ``DataFrame`` com uma linha por grupo e as colunas de
        :data:`COLUNAS_RESUMO`.

    Raises:
        EntradaInvalida: Se não houver grupos ou algum grupo estiver vazio.

    Example:
        >>> df = tabela_resumo({"controle": [2.0, 4.0, 6.0]})
        >>> float(df.loc[0, "media"]), float(df.loc[0, "desvio_padrao"])
        (4.0, 2.0)
    """
    _validar_grupos(grupos)
    linhas = []
    for nome, valores in grupos.items():
        arr = np.asarray(valores, dtype=float)
        n = int(arr.size)
        media = float(arr.mean())
        # ddof=1 exige n >= 2; com uma única medição a dispersão é indefinida.
        if n >= 2:
            desvio = float(arr.std(ddof=1))
            variancia = float(arr.var(ddof=1))
            erro = desvio / float(np.sqrt(n))
            cv = (desvio / media * 100) if media != 0 else float("nan")
        else:
            desvio = variancia = erro = cv = float("nan")
        linhas.append(
            {
                "grupo": nome,
                "n": n,
                "media": media,
                "desvio_padrao": desvio,
                "variancia": variancia,
                "erro_padrao": erro,
                "cv_percentual": cv,
                "minimo": float(arr.min()),
                "maximo": float(arr.max()),
            }
        )
    return pd.DataFrame(linhas, columns=COLUNAS_RESUMO)


def tabela_insumos(itens: Sequence[Mapping[str, object]]) -> pd.DataFrame:
    """Monta a tabela de insumos (reagentes/materiais) de um plano.

    Args:
        itens: Sequência de dicionários com ``nome``, ``unidade``,
            ``quantidade_base`` e ``quantidade_total``.

    Returns:
        ``DataFrame`` com essas colunas, ordenado por nome. Devolve um
        ``DataFrame`` vazio (com as colunas certas) se ``itens`` for vazio.
    """
    colunas = ["nome", "unidade", "quantidade_base", "quantidade_total"]
    if not itens:
        return pd.DataFrame(columns=colunas)
    return (
        pd.DataFrame(list(itens), columns=colunas)
        .sort_values("nome")
        .reset_index(drop=True)
    )


def _para_python(valor: Any) -> Any:
    """Converte um valor de célula em algo que o JSON aceite.

    Escalares do NumPy viram tipos nativos, e ``NaN``/``inf`` viram ``None`` —
    JSON não representa esses três, e a serialização falharia na camada de API.
    """
    if isinstance(valor, np.generic):
        valor = valor.item()
    if isinstance(valor, float) and not math.isfinite(valor):
        return None
    return valor


def para_registros(df: pd.DataFrame) -> list[dict]:
    """Converte um ``DataFrame`` em lista de dicionários serializável.

    Args:
        df: Tabela a converter.

    Returns:
        Lista de dicionários, uma entrada por linha, pronta para virar JSON.
    """
    return [
        {chave: _para_python(valor) for chave, valor in linha.items()}
        for linha in df.to_dict("records")
    ]


def exportar_csv(df: pd.DataFrame, caminho: str | Path) -> Path:
    """Salva a tabela em CSV, criando o diretório de destino se necessário.

    Usa vírgula como separador decimal e ponto e vírgula como delimitador —
    convenção do Excel em português, para o arquivo abrir já colunado.

    Args:
        df: Tabela a exportar.
        caminho: Caminho do arquivo ``.csv`` de destino.

    Returns:
        O caminho do arquivo gravado.
    """
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    return destino
