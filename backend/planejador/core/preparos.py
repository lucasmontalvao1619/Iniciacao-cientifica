"""Dimensionamento percentual; base científica registrada na ficha do protocolo."""

import math

from .exceptions import EntradaInvalida


def escalonar_formulacao(
    componentes: list, volume_base: float, volume_alvo: float
) -> list[dict]:
    """Escala componentes na mesma unidade da receita, sem somar massas e volumes."""
    for campo, valor in (
        ("Volume de referência", volume_base),
        ("Volume planejado", volume_alvo),
    ):
        if (
            isinstance(valor, bool)
            or not isinstance(valor, (int, float))
            or not math.isfinite(valor)
            or valor <= 0
        ):
            raise EntradaInvalida(f"{campo} deve ser positivo e finito.")
    if not isinstance(componentes, list) or not 1 <= len(componentes) <= 100:
        raise EntradaInvalida("Informe de 1 a 100 componentes da formulação.")
    fator = volume_alvo / volume_base
    nomes = set()
    saida = []
    for componente in componentes:
        if not isinstance(componente, dict):
            raise EntradaInvalida(
                "Cada componente deve informar nome, quantidade e unidade."
            )
        nome = componente.get("nome")
        q = componente.get("quantidade")
        unidade = componente.get("unidade")
        if (
            not isinstance(nome, str)
            or not nome.strip()
            or len(nome) > 160
            or nome.strip().casefold() in nomes
        ):
            raise EntradaInvalida(
                "Qual é o nome de cada componente? Use nomes distintos de até 160 caracteres."
            )
        nomes.add(nome.strip().casefold())
        if not isinstance(unidade, str) or unidade not in {"g", "mg", "mL", "µL"}:
            raise EntradaInvalida(
                "Qual é a unidade de cada componente: g, mg, mL ou µL?"
            )
        if (
            isinstance(q, bool)
            or not isinstance(q, (int, float))
            or not math.isfinite(q)
            or q <= 0
        ):
            raise EntradaInvalida(
                "Informe quantidade positiva e finita para cada componente da referência."
            )
        calculada = q * fator
        if not math.isfinite(calculada) or calculada <= 0:
            raise EntradaInvalida("O escalonamento excede a faixa numérica suportada.")
        saida.append(
            {"nome": nome.strip(), "quantidade_total": calculada, "unidade": unidade}
        )
    return saida


def preparar_percentual(
    base: str, concentracao: float, quantidade_final: float, pureza: float = 100
) -> dict:
    """Quantidade de reagente comercial em g ou mL, com teor na base declarada.

    Quantidade final em mL para m/v e v/v, em g para m/m. Não determina
    solubilidade, compatibilidade ou volume aditivo de solventes.
    """
    if base not in {"m/v", "v/v", "m/m"}:
        raise EntradaInvalida("Escolha massa/volume, volume/volume ou massa/massa.")
    for name, value in (
        ("Concentração", concentracao),
        ("Quantidade final", quantidade_final),
        ("Pureza/teor", pureza),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise EntradaInvalida(f"{name} deve ser um número.")
        if not math.isfinite(value) or value <= 0:
            raise EntradaInvalida(f"{name} deve ser positivo e finito.")
    if pureza > 100:
        raise EntradaInvalida("Pureza/teor não pode ultrapassar 100%.")
    if base in {"m/m", "v/v"} and concentracao > pureza:
        raise EntradaInvalida("A concentração desejada ultrapassa o teor do reagente.")
    puro = quantidade_final * (concentracao / 100)
    comercial = quantidade_final * (concentracao / pureza)
    if not math.isfinite(comercial) or comercial <= 0:
        raise EntradaInvalida("O cálculo excede a faixa numérica suportada.")
    return {
        "base": base,
        "quantidade_pura": puro,
        "quantidade_reagente": comercial,
        "unidade_reagente": "mL" if base == "v/v" else "g",
        "quantidade_final": quantidade_final,
        "unidade_final": "g" if base == "m/m" else "mL",
        "quantidade_solvente": quantidade_final - comercial if base == "m/m" else None,
    }


def preparar_molar(
    concentracao: float,
    quantidade_final: float,
    massa_molar: float,
    pureza: float = 100,
    forma: str = "pesagem",
    densidade: float | None = None,
) -> dict:
    """M em mol/L, volume final em mL, massa molar g/mol e teor % m/m.

    Para líquido medido por volume, a densidade é a do reagente comercial
    (g/mL), não a densidade do solvente. Não calcula especiação ou solubilidade.
    """
    for name, value in (
        ("Concentração molar", concentracao),
        ("Volume final", quantidade_final),
        ("Massa molar", massa_molar),
        ("Pureza/teor m/m", pureza),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise EntradaInvalida(f"{name} deve ser um número.")
        if not math.isfinite(value) or value <= 0:
            raise EntradaInvalida(f"{name} deve ser positivo e finito.")
    if pureza > 100:
        raise EntradaInvalida("Pureza/teor não pode ultrapassar 100% m/m.")
    if forma not in {"pesagem", "volume"}:
        raise EntradaInvalida("Escolha reagente pesado ou líquido medido por volume.")
    mols = concentracao * (quantidade_final / 1000)
    massa_pura = mols * massa_molar
    massa_comercial = massa_pura / (pureza / 100)
    if not all(
        math.isfinite(value) and value > 0
        for value in (mols, massa_pura, massa_comercial)
    ):
        raise EntradaInvalida("O cálculo excede a faixa numérica suportada.")
    quantidade = massa_comercial
    if forma == "volume":
        if isinstance(densidade, bool) or not isinstance(densidade, (int, float)):
            raise EntradaInvalida("Informe a densidade do reagente comercial em g/mL.")
        if not math.isfinite(densidade) or densidade <= 0:
            raise EntradaInvalida("A densidade deve ser positiva e finita.")
        quantidade = massa_comercial / densidade
        if not math.isfinite(quantidade) or quantidade <= 0:
            raise EntradaInvalida(
                "O volume de reagente excede a faixa numérica suportada."
            )
        if quantidade > quantidade_final:
            raise EntradaInvalida(
                "O volume de reagente calculado supera o volume final. Este preparo não concentra o reagente por remoção de solvente."
            )
    return {
        "base": "mol/L",
        "mols": mols,
        "quantidade_pura": massa_pura,
        "massa_reagente_g": massa_comercial,
        "quantidade_reagente": quantidade,
        "unidade_reagente": "mL" if forma == "volume" else "g",
        "quantidade_final": quantidade_final,
        "unidade_final": "mL",
        "quantidade_solvente": None,
    }


def preparar_estoque(
    unidade: str,
    concentracao: float,
    quantidade_final: float,
    correcao: str = "pureza",
    pureza: float | None = None,
    potencia: float | None = None,
    forma: str = "pesagem",
    densidade: float | None = None,
    equivalencia: float | None = None,
) -> dict:
    """Estoque massivo ou por atividade; quantidade final em mL.

    Potência em µg/mg exige concentração massiva; atividade em U/mg exige
    U/mL. Conversão U/µg exige equivalência específica informada; potência não é pureza química.
    """
    if unidade not in {"mg/mL", "µg/mL", "g/L", "U/mL"}:
        raise EntradaInvalida("Unidade de concentração de estoque não suportada.")
    for name, value in (
        ("Concentração do estoque", concentracao),
        ("Volume final", quantidade_final),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value <= 0
        ):
            raise EntradaInvalida(f"{name} deve ser positivo e finito.")
    if forma not in {"pesagem", "volume"}:
        raise EntradaInvalida("Escolha reagente pesado ou líquido medido por volume.")
    if correcao == "pureza" and unidade != "U/mL":
        if pureza is None:
            raise EntradaInvalida("Qual é a pureza do reagente em % m/m?")
        factor = 0.0001 if unidade == "µg/mL" else 0.1
        r = preparar_percentual("m/v", concentracao * factor, quantidade_final, pureza)
        massa = r["quantidade_reagente"]
        massa_pura = r["quantidade_pura"]
    elif (correcao == "potencia" and unidade != "U/mL") or (correcao == "atividade"):
        if (
            isinstance(potencia, bool)
            or not isinstance(potencia, (int, float))
            or not math.isfinite(potencia)
            or potencia <= 0
        ):
            raise EntradaInvalida(
                "Informe a potência/atividade positiva e finita do certificado do lote, na unidade indicada."
            )
        if correcao == "atividade" and unidade != "U/mL":
            if (
                isinstance(equivalencia, bool)
                or not isinstance(equivalencia, (int, float))
                or not math.isfinite(equivalencia)
                or equivalencia <= 0
            ):
                raise EntradaInvalida(
                    "Qual é a equivalência específica do certificado em U/µg? Não há fator universal."
                )
            potencia = potencia / equivalencia
            if not math.isfinite(potencia) or potencia <= 0:
                raise EntradaInvalida(
                    "A potência convertida excede a faixa numérica suportada."
                )
        c = concentracao if unidade in {"µg/mL", "U/mL"} else concentracao * 1000
        massa = (quantidade_final * c / potencia) / 1000
        massa_pura = None  # Potência/atividade não é uma fração de pureza química.
    else:
        raise EntradaInvalida(
            "A correção escolhida não é compatível com a unidade de concentração. U/mL requer U/mg; não há conversão universal entre U e µg."
        )
    if not math.isfinite(massa) or massa <= 0:
        raise EntradaInvalida("A massa calculada excede a faixa numérica suportada.")
    dose = massa * 1000
    if forma == "volume":
        if (
            isinstance(densidade, bool)
            or not isinstance(densidade, (int, float))
            or not math.isfinite(densidade)
            or densidade <= 0
        ):
            raise EntradaInvalida(
                "Informe a densidade positiva e finita do reagente comercial em g/mL."
            )
        dose = massa / densidade
        if not math.isfinite(dose) or dose <= 0 or dose > quantidade_final:
            raise EntradaInvalida(
                "O volume calculado de reagente não pode superar o volume final nem exceder a faixa numérica suportada."
            )
    if not math.isfinite(dose):
        raise EntradaInvalida("A dose calculada excede a faixa numérica suportada.")
    return {
        "base": unidade,
        "quantidade_pura": massa_pura,
        "massa_reagente_g": massa,
        "quantidade_reagente": dose,
        "unidade_reagente": "mL" if forma == "volume" else "mg",
        "quantidade_final": quantidade_final,
        "unidade_final": "mL",
        "quantidade_solvente": None,
        "correcao": correcao,
    }
