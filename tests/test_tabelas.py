"""Testes da organização dos dados em tabelas estruturadas."""

from __future__ import annotations

import math

import pytest

from planejador.core import tabelas
from planejador.core.exceptions import EntradaInvalida


def test_tabela_medicoes_formato_longo():
    df = tabelas.tabela_medicoes(
        {"controle": [1.0, 1.2], "tratamento": [2.0, 2.4, 2.8]}
    )
    assert list(df.columns) == ["grupo", "replicata", "valor"]
    assert len(df) == 5
    # replicatas numeradas a partir de 1, reiniciando a cada grupo
    controle = df[df["grupo"] == "controle"]
    assert list(controle["replicata"]) == [1, 2]


def test_tabela_resumo_valores_conferidos():
    # [2, 4, 6] -> média 4; desvio amostral 2; variância 4; CV = 2/4 = 50%
    df = tabelas.tabela_resumo({"controle": [2.0, 4.0, 6.0]})
    linha = df.iloc[0]
    assert int(linha["n"]) == 3
    assert math.isclose(float(linha["media"]), 4.0)
    assert math.isclose(float(linha["desvio_padrao"]), 2.0)
    assert math.isclose(float(linha["variancia"]), 4.0)
    assert math.isclose(float(linha["cv_percentual"]), 50.0)
    assert math.isclose(float(linha["minimo"]), 2.0)
    assert math.isclose(float(linha["maximo"]), 6.0)


def test_tabela_resumo_grupo_unico_valor_nao_quebra():
    df = tabelas.tabela_resumo({"unico": [5.0]})
    linha = df.iloc[0]
    assert int(linha["n"]) == 1
    assert math.isclose(float(linha["media"]), 5.0)
    # dispersão indefinida com n=1 -> NaN, não erro
    assert math.isnan(float(linha["desvio_padrao"]))


def test_tabela_resumo_media_zero_nao_divide_por_zero():
    df = tabelas.tabela_resumo({"g": [-1.0, 0.0, 1.0]})
    assert math.isnan(float(df.iloc[0]["cv_percentual"]))


def test_grupos_vazios_erro():
    with pytest.raises(EntradaInvalida):
        tabelas.tabela_medicoes({})
    with pytest.raises(EntradaInvalida, match="sem nenhuma medição"):
        tabelas.tabela_resumo({"controle": []})


def test_para_registros_troca_nan_por_none():
    df = tabelas.tabela_resumo({"unico": [5.0]})
    registros = tabelas.para_registros(df)
    assert registros[0]["desvio_padrao"] is None
    assert registros[0]["grupo"] == "unico"


def test_tabela_insumos_vazia_mantem_colunas():
    df = tabelas.tabela_insumos([])
    assert list(df.columns) == [
        "nome",
        "unidade",
        "quantidade_base",
        "quantidade_total",
    ]
    assert df.empty


def test_exportar_csv_grava_arquivo(tmp_path):
    df = tabelas.tabela_resumo({"controle": [2.0, 4.0, 6.0]})
    destino = tabelas.exportar_csv(df, tmp_path / "sub" / "resumo.csv")
    assert destino.exists()
    conteudo = destino.read_text(encoding="utf-8-sig")
    assert "grupo;n;media" in conteudo
    # separador decimal vírgula (convenção do Excel em português)
    assert "4,0" in conteudo
