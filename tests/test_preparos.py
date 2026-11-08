"""Casos de cálculo independentes para PREP-001 e seus limites."""

import json
from pathlib import Path

import pytest

from planejador.core.exceptions import EntradaInvalida
from planejador.core.preparos import preparar_percentual
from planejador.services.preparos import calcular_preparo


@pytest.mark.parametrize(
    "base,c,q,t,expected,solvent",
    [
        ("m/v", 0.9, 1000, 100, 9, None),
        ("m/v", 10, 200, 80, 25, None),
        ("v/v", 70, 100, 96, 72.91666666666667, None),
        ("m/m", 5, 200, 100, 10, 190),
        ("m/m", 10, 200, 80, 25, 175),
        ("m/v", 120, 100, 100, 120, None),
    ],
)
def test_percentual_independent_examples(base, c, q, t, expected, solvent):
    result = preparar_percentual(base, c, q, t)
    assert result["quantidade_reagente"] == pytest.approx(expected)
    assert result["quantidade_solvente"] == solvent
    # Balance independently recovers the requested fraction from the commercial dose.
    assert result["quantidade_reagente"] * (t / 100) / q * 100 == pytest.approx(c)


@pytest.mark.parametrize(
    "base,c,q,t",
    [
        ("m/v", 0, 100, 100),
        ("m/v", 1, -1, 100),
        ("m/v", 1, 100, 0),
        ("m/v", 1, 100, 101),
        ("v/v", 97, 100, 96),
        ("m/m", 101, 100, 100),
        ("bad", 1, 100, 100),
        ("m/v", float("nan"), 100, 100),
        ("m/v", 1, float("inf"), 100),
        ("m/v", 1, 100, float("inf")),
        ("m/v", True, 100, 100),
        ("m/v", "1", 100, 100),
        ("m/v", 1e308, 1e308, 100),
    ],
)
def test_percentual_rejects_invalid_or_nonfinite(base, c, q, t):
    with pytest.raises(EntradaInvalida):
        preparar_percentual(base, c, q, t)


def test_percentual_service_keeps_source_and_named_components():
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[0]
    params = {
        "base": "v/v",
        "concentracao": 70,
        "quantidade_final": 100,
        "pureza": 96,
        "soluto": "Etanol",
        "solvente": "Água",
    }
    plan = calcular_preparo(protocol, params)
    assert plan["fontes"][0]["isbn"] == "978-85-98768-41-0"
    assert plan["resultado"]["quantidade_solvente"] is None
    assert "q.s.p. 100 mL" in plan["solvente"]
    assert "Etanol" in plan["procedimento"][0]
    params["soluto"] = ""
    assert (
        calcular_preparo(protocol, params)["reagentes"][0]["nome"]
        == "Reagente não identificado"
    )
    params["soluto"] = 123
    with pytest.raises(EntradaInvalida):
        calcular_preparo(protocol, params)


@pytest.mark.parametrize(
    "c,v,mm,purity,expected",
    [
        (0.1, 1000, 58.44, 100, 5.844),
        (0.1, 500, 58.44, 100, 2.922),
        (0.2, 100, 100, 80, 2.5),
        (0.1, 100, 249.68, 100, 2.4968),
    ],
)
def test_molar_weighed_independent_cases(c, v, mm, purity, expected):
    from planejador.core.preparos import preparar_molar

    result = preparar_molar(c, v, mm, purity)
    assert result["quantidade_reagente"] == pytest.approx(expected)
    assert result["unidade_reagente"] == "g"
    assert result["mols"] == pytest.approx(c * v / 1000)
    assert result["quantidade_solvente"] is None


def test_molar_liquid_matches_fiocruz_2009_page_250():
    from planejador.core.preparos import preparar_molar

    result = preparar_molar(0.1, 1000, 36.5, 37, "volume", 1.19)
    # The source rounds the required commercial HCl dose to 8.29 mL.
    assert result["quantidade_reagente"] == pytest.approx(8.29, abs=0.005)
    assert result["massa_reagente_g"] == pytest.approx(9.86, abs=0.005)
    assert result["unidade_reagente"] == "mL"
    assert result["quantidade_reagente"] != pytest.approx(1000 - 8.29)


@pytest.mark.parametrize(
    "changes",
    [
        {"concentracao": 0},
        {"quantidade_final": -1},
        {"massa_molar": 0},
        {"massa_molar": float("nan")},
        {"pureza": 0},
        {"pureza": 101},
        {"forma": "unknown"},
        {"concentracao": float("inf")},
        {"massa_molar": "58.44"},
        {"pureza": True},
        {"forma": "volume", "densidade": None},
        {"forma": "volume", "densidade": 0},
        {"forma": "volume", "densidade": float("nan")},
        {"forma": "volume", "densidade": True},
        {"forma": "volume", "densidade": 0.001},
        {"concentracao": 1e308, "massa_molar": 1e308},
    ],
)
def test_molar_invalid_inputs(changes):
    from planejador.core.preparos import preparar_molar

    params = {
        "concentracao": 0.1,
        "quantidade_final": 1000,
        "massa_molar": 58.44,
        "pureza": 100,
    }
    params.update(changes)
    with pytest.raises(EntradaInvalida):
        preparar_molar(**params)


@pytest.mark.parametrize(
    "unit,c,purity,expected",
    [
        ("mg/mL", 2, 100, 200),
        ("g/L", 2, 100, 200),
        ("µg/mL", 2000, 100, 200),
        ("mg/mL", 2, 50, 400),
    ],
)
def test_stock_mass_units_and_purity(unit, c, purity, expected):
    from planejador.core.preparos import preparar_estoque

    r = preparar_estoque(unit, c, 100, pureza=purity)
    assert r["quantidade_reagente"] == pytest.approx(expected, rel=1e-12)
    assert r["unidade_reagente"] == "mg"
    assert r["quantidade_solvente"] is None


def test_stock_certificate_units_and_no_universal_equivalence():
    from decimal import Decimal

    from planejador.core.preparos import preparar_estoque

    expected = float(Decimal(10000) / Decimal(776))
    r = preparar_estoque("µg/mL", 10000, 1, "potencia", potencia=776)
    assert r["quantidade_reagente"] == pytest.approx(expected, rel=1e-12)
    assert r["quantidade_pura"] is None  # Potency does not establish chemical purity.
    # Source p. 110 prints 12.88 mg; the app retains the unrounded quotient.
    assert abs(r["quantidade_reagente"] - 12.88) < 0.01
    u = preparar_estoque("U/mL", 2000, 1, "atividade", potencia=2000)
    assert u["quantidade_reagente"] == 1
    with pytest.raises(EntradaInvalida, match="equivalência"):
        preparar_estoque("µg/mL", 10000, 1, "atividade", potencia=7760)
    converted = preparar_estoque(
        "µg/mL", 10000, 1, "atividade", potencia=7760, equivalencia=10
    )
    assert converted["quantidade_reagente"] == pytest.approx(expected, rel=1e-12)
    changed = preparar_estoque(
        "µg/mL", 10000, 1, "atividade", potencia=7760, equivalencia=20
    )
    assert changed["quantidade_reagente"] == pytest.approx(expected * 2, rel=1e-12)


@pytest.mark.parametrize(
    "changes",
    [
        {"unidade": "bad"},
        {"concentracao": 0},
        {"quantidade_final": -1},
        {"concentracao": float("nan")},
        {"pureza": 0},
        {"pureza": 101},
        {"correcao": "potencia"},
        {"correcao": "potencia", "potencia": float("inf")},
        {"correcao": "atividade", "potencia": 1000, "equivalencia": 0},
        {"correcao": "atividade", "potencia": 1000, "equivalencia": float("nan")},
        {"correcao": "atividade", "potencia": 1000, "equivalencia": True},
        {"unidade": "U/mL", "correcao": "pureza"},
        {"unidade": "U/mL", "correcao": "potencia", "potencia": 1000},
        {"forma": "volume", "densidade": None},
        {"forma": "volume", "densidade": 0.000001},
        {"forma": "unknown"},
    ],
)
def test_stock_invalid_or_incompatible_inputs(changes):
    from planejador.core.preparos import preparar_estoque

    params = {
        "unidade": "mg/mL",
        "concentracao": 2,
        "quantidade_final": 100,
        "pureza": 100,
    }
    params.update(changes)
    with pytest.raises(EntradaInvalida):
        preparar_estoque(**params)


def test_stock_optional_label_data_never_invents_identity_or_validity():
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[2]
    params = {
        "unidade_concentracao": "mg/mL",
        "concentracao": 2,
        "quantidade_final": 100,
        "correcao": "pureza",
        "pureza": 100,
        "forma": "pesagem",
        "solvente": "Solvente A",
        "diluente": "Diluente B",
    }
    plan = calcular_preparo(protocol, params)
    assert plan["reagentes"][0]["nome"] == "Reagente não identificado"
    assert plan["solvente"] == "Diluente B q.s.p. 100 mL de solução"
    assert plan["rotulo_planejado"]["data_validade"] == ""
    assert plan["pendencias_rotulo"] and plan["erros_rotulo"] == {}
    params.update(data_preparo="2026-11-08", data_validade="2026-11-07")
    plan = calcular_preparo(protocol, params)
    assert "data_validade" in plan["erros_rotulo"]
    assert plan["resultado"]["quantidade_reagente"] == pytest.approx(200)
    params["data_validade"] = "20261130"
    assert "data_validade" in calcular_preparo(protocol, params)["erros_rotulo"]
    params.update(
        data_validade="2026-11-30",
        fonte_estabilidade="Método informado pelo pesquisador",
    )
    assert calcular_preparo(protocol, params)["erros_rotulo"] == {}


def test_stock_never_assumes_missing_purity():
    from planejador.core.preparos import preparar_estoque

    with pytest.raises(EntradaInvalida):
        preparar_estoque("mg/mL", 2, 100)
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[2]
    with pytest.raises(EntradaInvalida):
        calcular_preparo(
            protocol,
            {
                "unidade_concentracao": "mg/mL",
                "concentracao": 2,
                "quantidade_final": 100,
                "correcao": "pureza",
                "forma": "pesagem",
            },
        )


@pytest.mark.parametrize(
    "unit,c1,c2,v,expected",
    [
        ("mol/L", 1, 0.1, 10, 1),
        ("mg/mL", 10, 1, 100, 10),
        ("µg/mL", 200, 20, 50, 5),
        ("% v/v", 70, 35, 100, 50),
        ("mg/mL", 1, 1, 5, 5),
    ],
)
def test_stock_dilution_independent_cases(unit, c1, c2, v, expected):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[3]
    plan = calcular_preparo(
        protocol,
        {
            "unidade_concentracao": unit,
            "concentracao_inicial": c1,
            "concentracao": c2,
            "quantidade_final": v,
        },
    )
    r = plan["resultado"]
    assert r["quantidade_reagente"] == pytest.approx(expected)
    assert c1 * r["quantidade_reagente"] == pytest.approx(c2 * v)
    assert r["volume_diluente_nominal"] == pytest.approx(v - expected)
    assert plan["solvente"].startswith("Solvente não informado q.s.p.")
    assert plan["fontes"] and not plan["pendente"]


@pytest.mark.parametrize(
    "changes",
    [
        {"concentracao_inicial": 0},
        {"concentracao": float("nan")},
        {"quantidade_final": float("inf")},
        {"concentracao_inicial": True},
        {"concentracao": "1"},
        {"concentracao": 11},
        {"unidade_concentracao": "% m/m"},
        {"unidade_concentracao": []},
        {"unidade_concentracao": "% v/v", "concentracao_inicial": 101},
        {"concentracao_inicial": 1e308, "concentracao": 1e-308},
    ],
)
def test_stock_dilution_rejects_bad_inputs(changes):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[3]
    params = {
        "unidade_concentracao": "mg/mL",
        "concentracao_inicial": 10,
        "concentracao": 1,
        "quantidade_final": 100,
    }
    params.update(changes)
    with pytest.raises(EntradaInvalida):
        calcular_preparo(protocol, params)


@pytest.mark.parametrize(
    "factor,n,equalize",
    [
        (10, 3, False),
        (2, 3, False),
        (2, 3, True),
        (10, 1, False),
        (10, 1, True),
        (1.5, 100, False),
    ],
)
def test_serial_balances_and_remaining_volumes(factor, n, equalize):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[4]
    c0, volume = 100, 10
    plan = calcular_preparo(
        protocol,
        {
            "unidade_concentracao": "mg/mL",
            "concentracao_inicial": c0,
            "fator": factor,
            "n_diluicoes": n,
            "quantidade_final": volume,
            "igualar_ultimo": equalize,
        },
    )
    steps = plan["etapas"]
    a = volume / factor
    assert len(steps) == n
    for i, step in enumerate(steps, 1):
        assert step["concentracao"] == pytest.approx(c0 / (factor**i))
        source = c0 if i == 1 else steps[i - 2]["concentracao"]
        assert source * a == pytest.approx(step["concentracao"] * volume)
        assert step["volume_restante_mL"] == pytest.approx(
            volume - a if i < n or equalize else volume
        )
    removed = a if equalize else 0
    assert a + plan["resultado"]["diluente_total_nominal_mL"] == pytest.approx(
        sum(s["volume_restante_mL"] for s in steps) + removed
    )
    assert c0 * a == pytest.approx(
        sum(s["concentracao"] * s["volume_restante_mL"] for s in steps)
        + removed * steps[-1]["concentracao"]
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"fator": 1},
        {"fator": float("nan")},
        {"fator": float("inf")},
        {"fator": True},
        {"n_diluicoes": 0},
        {"n_diluicoes": 101},
        {"n_diluicoes": 2.5},
        {"n_diluicoes": True},
        {"concentracao_inicial": 0},
        {"quantidade_final": -1},
        {"igualar_ultimo": "sim"},
        {"unidade_concentracao": "% m/m"},
        {"unidade_concentracao": "% v/v", "concentracao_inicial": 101},
        {"concentracao_inicial": 1e-300, "fator": 100000, "n_diluicoes": 100},
    ],
)
def test_serial_rejects_bad_or_unrepresentable_inputs(changes):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[4]
    params = {
        "unidade_concentracao": "mg/mL",
        "concentracao_inicial": 100,
        "fator": 10,
        "n_diluicoes": 3,
        "quantidade_final": 10,
    }
    params.update(changes)
    with pytest.raises(EntradaInvalida):
        calcular_preparo(protocol, params)


@pytest.mark.parametrize(
    "c0,a,v,expected,factor",
    [
        (1, 1, 10, 0.1, 10),
        (100, 2, 50, 4, 25),
        (70, 50, 100, 35, 2),
        (1, 5, 5, 1, 1),
        (1e308, 10, 100, 1e307, 10),
    ],
)
def test_final_concentration_from_volumes_independent(c0, a, v, expected, factor):
    from planejador.core.calculos import diluicao_por_volumes

    c2, r = diluicao_por_volumes(c0, a, v)
    assert c2 == pytest.approx(expected)
    assert r.fator_diluicao == pytest.approx(factor)
    assert r.volume_alicota == a and r.volume_final == v
    assert c2 / c0 == pytest.approx(a / v)
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[5]
    plan = calcular_preparo(
        protocol,
        {
            "unidade_concentracao": "mg/mL",
            "concentracao_inicial": c0,
            "volume_alicota": a,
            "quantidade_final": v,
        },
    )
    assert plan["resultado"]["concentracao_calculada"] == pytest.approx(expected)
    assert plan["concentracao_nominal"]["valor"] == pytest.approx(expected)
    assert plan["resultado"]["volume_diluente_nominal"] == v - a
    assert "q.s.p." in plan["solvente"]


@pytest.mark.parametrize(
    "changes",
    [
        {"concentracao_inicial": 0},
        {"volume_alicota": 0},
        {"quantidade_final": -1},
        {"volume_alicota": 11},
        {"volume_alicota": float("nan")},
        {"quantidade_final": float("inf")},
        {"volume_alicota": True},
        {"concentracao_inicial": "1"},
        {"unidade_concentracao": "% m/m"},
        {"unidade_concentracao": "% v/v", "concentracao_inicial": 101},
        {"volume_alicota": 1e-308, "quantidade_final": 1e308},
    ],
)
def test_factor_concentration_rejects_invalid_inputs(changes):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[5]
    params = {
        "unidade_concentracao": "mg/mL",
        "concentracao_inicial": 100,
        "volume_alicota": 1,
        "quantidade_final": 10,
    }
    params.update(changes)
    with pytest.raises(EntradaInvalida):
        calcular_preparo(protocol, params)


@pytest.mark.parametrize(
    "v,n,e,base,total",
    [
        (20, 10, 10, 200, 220),
        (2.5, 4, 0, 10, 10),
        (1, 1, 25, 1, 1.25),
        (0.001, 1000000, 10, 1000, 1100),
    ],
)
def test_volume_totals_independent(v, n, e, base, total):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[6]
    plan = calcular_preparo(
        protocol,
        {
            "volume_unitario": v,
            "n_unidades": n,
            "excesso_percentual": e,
            "unidade_volume": "mL",
        },
    )
    r = plan["resultado"]
    assert r["volume_sem_excedente"] == pytest.approx(base)
    assert r["quantidade_final"] == pytest.approx(total)
    assert r["volume_excedente"] == pytest.approx(total - base)
    assert r["quantidade_final"] == pytest.approx(
        r["volume_sem_excedente"] + r["volume_excedente"]
    )
    assert plan["reagentes"][0]["quantidade_total"] == pytest.approx(total)


@pytest.mark.parametrize(
    "changes",
    [
        {"volume_unitario": 0},
        {"n_unidades": 0},
        {"n_unidades": 1.5},
        {"n_unidades": True},
        {"n_unidades": 1000001},
        {"excesso_percentual": -1},
        {"excesso_percentual": float("nan")},
        {"excesso_percentual": float("inf")},
        {"excesso_percentual": True},
        {"volume_unitario": float("nan")},
        {"volume_unitario": True},
        {"unidade_volume": "g"},
        {"volume_unitario": 1e308, "n_unidades": 10},
    ],
)
def test_volume_rejects_invalid_inputs(changes):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[6]
    params = {
        "volume_unitario": 20,
        "n_unidades": 10,
        "excesso_percentual": 10,
        "unidade_volume": "µL",
    }
    params.update(changes)
    with pytest.raises(EntradaInvalida):
        calcular_preparo(protocol, params)


def test_reference_formula_scaling_and_attribution():
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[7]
    params = {"formulacao_id": "anvisa_agar_nutriente", "volume_alvo_mL": 250}
    plan = calcular_preparo(protocol, params)
    assert [x["quantidade_total"] for x in plan["reagentes"]] == pytest.approx(
        [0.75, 1.25, 3.75, 250]
    )
    assert [x["unidade"] for x in plan["reagentes"]] == ["g", "g", "g", "mL"]
    assert "6,8" in plan["condicoes_preparo"]["ph"] and plan["pendencias_preparo"]
    assert "4 a 8" in plan["condicoes_preparo"]["conservacao"]
    assert plan["resultado"]["fator_escala"] == 0.25
    assert "ANVISA" in plan["formula_origem"]
    params["componentes"] = [{"nome": "Outro", "quantidade": 1, "unidade": "g"}]
    with pytest.raises(EntradaInvalida):
        calcular_preparo(protocol, params)


def test_custom_formula_preserves_units_and_researcher_source():
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[7]
    params = {
        "formulacao_id": "pesquisador",
        "fonte_formula": "Formulação própria, versão 1",
        "volume_base_mL": 100,
        "volume_alvo_mL": 150,
        "componentes": [
            {"nome": "A", "quantidade": 3, "unidade": "mg"},
            {"nome": "B", "quantidade": 2, "unidade": "µL"},
        ],
        "ph": "6,2 a 25 °C",
        "procedimento_formula": "Procedimento informado pelo pesquisador",
        "ciclo": "Ciclo validado informado pelo laboratório",
        "conservacao": "Método do laboratório",
    }
    plan = calcular_preparo(protocol, params)
    assert [x["quantidade_total"] for x in plan["reagentes"]] == pytest.approx([4.5, 3])
    assert [x["unidade"] for x in plan["reagentes"]] == ["mg", "µL"]
    assert (
        "pesquisador" in plan["formula_origem"]
        and "não validada" in plan["formula_origem"]
    )
    assert (
        plan["condicoes_preparo"]["ph"] == params["ph"]
        and not plan["pendencias_preparo"]
    )
    params["fonte_formula"] = ""
    with pytest.raises(EntradaInvalida):
        calcular_preparo(protocol, params)


@pytest.mark.parametrize(
    "components,base,target",
    [
        ([], 100, 10),
        ([{"nome": "A", "quantidade": 1, "unidade": "g"}], 0, 10),
        ([{"nome": "A", "quantidade": 1, "unidade": "g"}], 100, float("inf")),
        ([{"nome": "A", "quantidade": True, "unidade": "g"}], 100, 10),
        ([{"nome": "A", "quantidade": float("nan"), "unidade": "g"}], 100, 10),
        ([{"nome": "A", "quantidade": -1, "unidade": "g"}], 100, 10),
        ([{"nome": "A", "quantidade": 1, "unidade": "kg"}], 100, 10),
        ([{"nome": "", "quantidade": 1, "unidade": "g"}], 100, 10),
        (
            [
                {"nome": "A", "quantidade": 1, "unidade": "g"},
                {"nome": " a ", "quantidade": 1, "unidade": "g"},
            ],
            100,
            10,
        ),
        ([{"nome": "A", "quantidade": 1e308, "unidade": "g"}], 1, 100),
        ([{"nome": "A", "quantidade": 1, "unidade": "g"}], 1e308, 1e-308),
    ],
)
def test_formula_rejects_invalid_inputs(components, base, target):
    from planejador.core.preparos import escalonar_formulacao

    with pytest.raises(EntradaInvalida):
        escalonar_formulacao(components, base, target)


@pytest.mark.parametrize("basis", ["agua", "final"])
def test_commercial_medium_scales_label_proportion(basis):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[8]
    params = {
        "massa_referencia_g": 26,
        "volume_referencia_mL": 1000,
        "volume_alvo_mL": 250,
        "tipo_volume": basis,
        "referencia_fabricante": "Documento declarado para teste, versão 1",
    }
    plan = calcular_preparo(protocol, params)
    assert plan["resultado"]["quantidade_reagente"] == pytest.approx(6.5)
    assert plan["resultado"]["fator_escala"] == 0.25
    assert ("q.s.p." in plan["solvente"]) == (basis == "final")
    assert plan["fonte_fabricante_declarada"]["consulta_declarada"] == ""
    assert "pesquisador" in plan["fonte_fabricante_declarada"]["origem"]
    assert plan["pendencias_preparo"] and plan["condicoes_preparo"]["ciclo"] == ""


@pytest.mark.parametrize(
    "changes",
    [
        {"massa_referencia_g": 0},
        {"massa_referencia_g": True},
        {"volume_referencia_mL": 0},
        {"volume_alvo_mL": float("nan")},
        {"volume_alvo_mL": float("inf")},
        {"tipo_volume": None},
        {"tipo_volume": "desconhecido"},
        {"referencia_fabricante": ""},
        {"referencia_fabricante": 123},
        {"ciclo": []},
        {"massa_referencia_g": 1e308, "volume_alvo_mL": 1e308},
    ],
)
def test_commercial_medium_rejects_invalid_inputs(changes):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[8]
    params = {
        "massa_referencia_g": 26,
        "volume_referencia_mL": 1000,
        "volume_alvo_mL": 250,
        "tipo_volume": "agua",
        "referencia_fabricante": "Documento declarado para teste",
    }
    params.update(changes)
    with pytest.raises(EntradaInvalida):
        calcular_preparo(protocol, params)


def test_medium_by_recipients_independent_values_and_declared_method():
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[9]
    params = {
        "recipiente": "placas",
        "soluto": "Meio definido pelo pesquisador",
        "unidade_volume": "mL",
        "volume_unitario": 20,
        "n_unidades": 12,
        "excesso_percentual": 10,
        "formato_recipiente": "90 mm",
        "metodo_distribuicao": "Método próprio v1",
    }
    plan = calcular_preparo(protocol, params)
    assert plan["tipo_calculo"] == "recipientes"
    assert plan["resultado"]["volume_sem_excedente"] == 240
    assert plan["resultado"]["volume_excedente"] == 24
    assert plan["resultado"]["quantidade_final"] == 264
    assert not plan["pendencias_preparo"]
    assert plan["distribuicao"]["metodo_distribuicao"] == "Método próprio v1"
    assert plan["fontes"][0]["paginas_pdf"] == [20]
    params.update(
        recipiente="tubos",
        volume_unitario=6,
        n_unidades=10,
        excesso_percentual=0,
        formato_recipiente="",
        metodo_distribuicao="",
    )
    plan = calcular_preparo(protocol, params)
    assert plan["resultado"]["quantidade_final"] == 60
    assert plan["resultado"]["volume_excedente"] == 0
    assert len(plan["pendencias_preparo"]) == 2
    assert plan["recipiente"] == "tubos"


@pytest.mark.parametrize(
    "field,value",
    [
        ("recipiente", None),
        ("recipiente", []),
        ("recipiente", "poços"),
        ("n_unidades", 0),
        ("n_unidades", True),
        ("n_unidades", 1.5),
        ("volume_unitario", 0),
        ("volume_unitario", float("inf")),
        ("excesso_percentual", -1),
        ("excesso_percentual", float("nan")),
        ("unidade_volume", "g"),
        ("formato_recipiente", 9),
        ("metodo_distribuicao", "a" * 2001),
    ],
)
def test_medium_by_recipients_rejects_invalid_answers(field, value):
    protocol = json.loads(
        (Path(__file__).parents[1] / "frontend/protocolos.json").read_text()
    )[9]
    params = {
        "recipiente": "placas",
        "unidade_volume": "mL",
        "volume_unitario": 20,
        "n_unidades": 12,
        "excesso_percentual": 0,
    }
    params[field] = value
    with pytest.raises(EntradaInvalida):
        calcular_preparo(protocol, params)
