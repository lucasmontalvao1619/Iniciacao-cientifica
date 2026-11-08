"""Plano rastreável de preparo, separado da seleção de widgets e das medições."""

from planejador.core.exceptions import EntradaInvalida
from planejador.core.preparos import (
    preparar_estoque,
    preparar_molar,
    preparar_percentual,
)


def calcular_preparo(protocolo: dict, parametros: dict) -> dict:
    if protocolo.get("tipo_calculo") not in {
        "percentual",
        "molar",
        "estoque",
        "diluicao",
        "seriada",
        "fator",
        "volume",
        "formula",
        "desidratado",
        "recipientes",
    }:
        raise EntradaInvalida(
            "As regras deste protocolo ainda não estão implementadas."
        )
    for field in ("soluto", "solvente", "diluente"):
        value = parametros.get(field, "")
        if not isinstance(value, str) or len(value) > 160:
            raise EntradaInvalida(
                f"A identificação de {field} deve ser texto com até 160 caracteres."
            )
    if protocolo["tipo_calculo"] == "seriada":
        return _calcular_seriada(protocolo, parametros)
    if protocolo["tipo_calculo"] == "recipientes":
        return _calcular_recipientes(protocolo, parametros)
    if protocolo["tipo_calculo"] == "volume":
        return _calcular_volume(protocolo, parametros)
    if protocolo["tipo_calculo"] == "formula":
        return _calcular_formula(protocolo, parametros)
    if protocolo["tipo_calculo"] == "desidratado":
        return _calcular_desidratado(protocolo, parametros)
    estoque = protocolo["tipo_calculo"] == "estoque"
    inverso = protocolo["tipo_calculo"] == "fator"
    diluicao = protocolo["tipo_calculo"] in {"diluicao", "fator"}
    molar = protocolo["tipo_calculo"] == "molar" or (
        estoque and parametros.get("unidade_concentracao") == "mol/L"
    )
    if estoque and molar and parametros.get("correcao", "pureza") != "pureza":
        raise EntradaInvalida(
            "Concentração em mol/L requer teor % m/m e massa molar; não há conversão automática de potência em molaridade."
        )
    if diluicao:
        from planejador.core.calculos import diluicao_por_volumes, preparar_diluicao

        unit = parametros.get("unidade_concentracao")
        if not isinstance(unit, str) or unit not in {
            "mg/mL",
            "µg/mL",
            "g/L",
            "mol/L",
            "mmol/L",
            "U/mL",
            "% m/v",
            "% v/v",
        }:
            raise EntradaInvalida(
                "Escolha a mesma unidade por volume para as duas concentrações; % m/m não se aplica a esta fórmula."
            )
        if unit == "% v/v" and any(
            isinstance(parametros.get(key), (int, float)) and parametros[key] > 100
            for key in (
                ("concentracao_inicial",)
                if inverso
                else ("concentracao_inicial", "concentracao")
            )
        ):
            raise EntradaInvalida("Concentração em % v/v não pode ultrapassar 100%.")
        if inverso:
            c2, r = diluicao_por_volumes(
                parametros.get("concentracao_inicial", 0),
                parametros.get("volume_alicota", 0),
                parametros.get("quantidade_final", 0),
            )
        else:
            r = preparar_diluicao(
                parametros.get("concentracao_inicial", 0),
                parametros.get("concentracao", 0),
                parametros.get("quantidade_final", 0),
            )
        result = {
            "base": unit,
            "quantidade_pura": None,
            "quantidade_reagente": r.volume_alicota,
            "unidade_reagente": "mL",
            "quantidade_final": r.volume_final,
            "unidade_final": "mL",
            "quantidade_solvente": None,
            "fator_diluicao": r.fator_diluicao,
            "volume_diluente_nominal": r.volume_diluente,
        }
        if inverso:
            result["concentracao_calculada"] = c2
    elif molar:
        result = preparar_molar(
            parametros["concentracao"],
            parametros["quantidade_final"],
            parametros["massa_molar"],
            parametros["pureza"],
            parametros["forma"],
            parametros.get("densidade"),
        )
    elif estoque:
        result = preparar_estoque(
            parametros["unidade_concentracao"],
            parametros["concentracao"],
            parametros["quantidade_final"],
            parametros["correcao"],
            parametros.get("pureza"),
            parametros.get("potencia"),
            parametros["forma"],
            parametros.get("densidade"),
            parametros.get("equivalencia"),
        )
    else:
        result = preparar_percentual(
            parametros["base"],
            parametros["concentracao"],
            parametros["quantidade_final"],
            parametros["pureza"],
        )
    soluto = parametros.get("soluto", "").strip() or (
        "Solução-estoque não identificada" if diluicao else "Reagente não identificado"
    )
    solvente = parametros.get("solvente", "").strip() or "Solvente não informado"
    diluente = (
        (parametros.get("diluente", "").strip() or solvente) if estoque else solvente
    )
    dose = f"{result['quantidade_reagente']:.6g} {result['unidade_reagente']}"
    target = f"{result['quantidade_final']:.6g} {result['unidade_final']}"
    solvent = (
        f"{result['quantidade_solvente']:.6g} g de {solvente}"
        if result["quantidade_solvente"] is not None
        else f"{diluente} q.s.p. {target} de solução"
    )
    steps = [
        f"Conferir a identificação, teor e FDS de {soluto} e {solvente}; confirmar compatibilidade e solubilidade para a finalidade do experimento.",
        f"Medir {dose} de {soluto}, com instrumento apropriado à massa ou ao volume. Para pesagem, verificar nivelamento e calibração da balança.",
        f"Transferir quantitativamente para recipiente limpo e adequado e dissolver com {solvente}, na quantidade e nas condições recomendadas pelo método do experimento, evitando contaminação do frasco original.",
        f"Preparar com {solvent}. "
        + (
            "A massa final inclui o reagente comercial e o solvente."
            if result["base"] == "m/m"
            else "Completar até a marca final; não interpretar a diferença de volumes como volume exato de solvente."
        ),
        "Homogeneizar e identificar o preparo; seguir requisitos específicos de armazenamento, estabilidade e segurança do experimento e das substâncias.",
    ]
    if molar:
        steps.insert(
            1,
            "Conferir que a massa molar e o teor correspondem à forma química do rótulo (anidra ou hidratada); para reagente líquido, usar sua densidade na temperatura aplicável. Se for exigida concentração exata, verificar a necessidade de padronização pelo método do experimento.",
        )
        steps[4] = (
            f"Completar com {solvent} em balão volumétrico adequado, somente após dissolução e equilíbrio térmico conforme o método. Não subtrair volumes como se fossem aditivos."
        )
    plan = {
        "protocolo": f"{protocolo['id']} · {protocolo['name']}",
        "protocolo_id": protocolo["id"],
        "tipo_calculo": protocolo["tipo_calculo"],
        "pendente": False,
        "resultado": result,
        "reagentes": [
            {
                "nome": soluto,
                "quantidade_total": result["quantidade_reagente"],
                "unidade": result["unidade_reagente"],
            },
        ],
        "materiais": [],
        "equipamentos": protocolo.get("equipamentos", []),
        "solvente": solvent,
        "procedimento": steps,
        "fontes": protocolo["fontes"],
        "limites": "Dimensionamento planejado. Não verifica solubilidade, compatibilidade, tolerância da vidraria, estabilidade, esterilidade ou adequação a uso clínico.",
    }

    if diluicao:
        plan["procedimento"] = [
            "Conferir concentração real do estoque, unidade comum das concentrações, compatibilidade do diluente e requisitos do método.",
            f"Transferir {dose} de {soluto} com instrumento volumétrico adequado à alíquota e à tolerância requerida.",
            f"Completar com {solvent} em vidraria adequada, nas condições térmicas do método; não medir o diluente somente pela subtração dos volumes.",
            "Homogeneizar e identificar concentração, conteúdo e condições de conservação conforme o método da substância.",
        ]
        plan["concentracao_estoque"] = {
            "valor": parametros["concentracao_inicial"],
            "unidade": unit,
        }
        plan["concentracao_nominal"] = {
            "valor": c2 if inverso else parametros["concentracao"],
            "unidade": unit,
        }
        plan["observacao_diluicao"] = (
            "As concentrações são iguais: fator 1, sem necessidade de diluição."
            if result["fator_diluicao"] == 1
            else "A diferença entre volume final e alíquota é nominal; completar q.s.p. ao volume final."
        )
        if inverso:
            plan["observacao_diluicao"] = (
                f"Concentração final calculada: {c2:.6g} {unit}. "
                + plan["observacao_diluicao"]
            )

    if estoque:
        from datetime import date

        keys = (
            "identificacao_estoque",
            "responsavel",
            "lote_reagente",
            "data_preparo",
            "data_validade",
            "armazenamento",
            "fonte_estabilidade",
        )
        metadata = {}
        for key in keys:
            value = parametros.get(key, "")
            if not isinstance(value, str) or len(value) > 300:
                raise EntradaInvalida(
                    "Os dados de identificação/conservação devem ser textos de até 300 caracteres."
                )
            metadata[key] = value.strip()
        errors = {}
        dates = {}
        for key in ("data_preparo", "data_validade"):
            if metadata[key]:
                try:
                    parsed = date.fromisoformat(metadata[key])
                    if parsed.isoformat() != metadata[key]:
                        raise ValueError("Formato não canônico")
                    dates[key] = parsed
                except ValueError:
                    errors[key] = "Qual é a data válida no formato AAAA-MM-DD?"
        if (
            dates.get("data_preparo")
            and dates.get("data_validade")
            and dates["data_validade"] < dates["data_preparo"]
        ):
            errors["data_validade"] = (
                "Qual é a validade correta? A informada é anterior ao preparo previsto."
            )
        if metadata["data_validade"] and not metadata["fonte_estabilidade"]:
            errors["fonte_estabilidade"] = (
                "Qual método ou fonte fundamenta a validade informada?"
            )
        plan["erros_rotulo"] = errors
        plan["rotulo_planejado"] = metadata
        plan["pendencias_rotulo"] = [
            key for key, value in metadata.items() if not value
        ]
        plan["solvente_dissolucao"] = solvente
        plan["diluente_final"] = diluente
        plan["concentracao_nominal"] = {
            "valor": parametros["concentracao"],
            "unidade": parametros["unidade_concentracao"],
        }
        steps.insert(
            1,
            "Conferir o certificado do lote: teor químico, potência em µg/mg e atividade em U/mg são bases distintas. Não aplicar um fator universal entre U e µg.",
        )
        steps.append(
            "Identificar e conservar o estoque conforme o método e a substância. Os dados ausentes de rótulo permanecem pendentes; o aplicativo não calcula prazo de validade nem define temperatura universal de armazenamento."
        )
    return plan


def _calcular_desidratado(protocolo: dict, parametros: dict) -> dict:
    from planejador.core.preparos import escalonar_formulacao

    texts = {}
    for key in (
        "referencia_fabricante",
        "consulta_fabricante",
        "procedimento_fabricante",
        "ph",
        "ciclo",
        "suplementos",
        "conservacao",
    ):
        value = parametros.get(key, "")
        if not isinstance(value, str) or len(value) > 2000:
            raise EntradaInvalida(
                "As respostas sobre a instrução devem ter até 2000 caracteres."
            )
        texts[key] = value.strip()
    if not texts["referencia_fabricante"]:
        raise EntradaInvalida(
            "Qual rótulo/documento e versão fundamentam a proporção informada?"
        )
    convention = parametros.get("tipo_volume")
    if convention not in ("agua", "final"):
        raise EntradaInvalida(
            "A instrução do fabricante se refere ao volume de água ou ao volume final?"
        )
    base = parametros.get("volume_referencia_mL", 0)
    target = parametros.get("volume_alvo_mL", 0)
    name = parametros.get("soluto", "").strip() or "Meio comercial não identificado"
    ingredients = escalonar_formulacao(
        [
            {
                "nome": name,
                "quantidade": parametros.get("massa_referencia_g", 0),
                "unidade": "g",
            }
        ],
        base,
        target,
    )
    mass = ingredients[0]["quantidade_total"]
    water = (
        f"{target:g} mL de água, conforme instrução, sem tratar como volume final exato"
        if convention == "agua"
        else f"água q.s.p. {target:g} mL finais, conforme instrução"
    )
    pending = [
        question
        for key, question in (
            (
                "procedimento_fabricante",
                "Qual procedimento de hidratação/preparo acompanha o produto?",
            ),
            ("ph", "Qual pH e condição de medida se aplicam?"),
            ("ciclo", "Qual processo/ciclo de esterilização se aplica?"),
            (
                "suplementos",
                "Quais suplementos/adições são exigidos, ou a instrução informa nenhum?",
            ),
            ("conservacao", "Quais condições de conservação/validade se aplicam?"),
        )
        if not texts[key]
    ]
    return {
        "protocolo": f"{protocolo['id']} · {protocolo['name']}",
        "protocolo_id": protocolo["id"],
        "tipo_calculo": "desidratado",
        "pendente": False,
        "resultado": {
            "quantidade_reagente": mass,
            "unidade_reagente": "g",
            "quantidade_final": target,
            "unidade_final": "mL",
            "fator_escala": target / base,
        },
        "tipo_volume": convention,
        "fonte_fabricante_declarada": {
            "referencia": texts["referencia_fabricante"],
            "consulta_declarada": texts["consulta_fabricante"],
            "origem": "Informada pelo pesquisador; não consultada automaticamente pelo aplicativo",
        },
        "condicoes_preparo": texts,
        "pendencias_preparo": pending,
        "reagentes": ingredients,
        "materiais": [],
        "equipamentos": protocolo.get("equipamentos", []),
        "solvente": water,
        "procedimento": [
            f"Conferir o produto e a instrução informada pelo pesquisador: {texts['referencia_fabricante']}.",
            f"Proporção informada: {parametros['massa_referencia_g']:g} g para {base:g} mL ({'água' if convention == 'agua' else 'volume final'}). Fator {target / base:g}; pesar {mass:.6g} g.",
            f"Preparar com {water}. Seguir hidratação, aquecimento e sequência de adições descritos na instrução, sem presumir ciclo universal.",
            *[
                f"{label}: {texts[key] or 'pendente de resposta do pesquisador'}."
                for key, label in (
                    ("procedimento_fabricante", "Procedimento informado"),
                    ("ph", "pH/medida informados"),
                    ("ciclo", "Processo/ciclo informado"),
                    ("suplementos", "Suplementos/adições informados"),
                    ("conservacao", "Conservação/validade informadas"),
                )
            ],
            "Conferir qualidade do meio e requisitos do método antes do uso.",
        ],
        "fontes": protocolo["fontes"],
        "limites": "Cálculo da massa nominal do pó a partir da proporção declarada. Não valida instrução, marca, composição, suplementos, ciclo ou estabilidade. Volume de água não é convertido em volume final; sem validação em bancada.",
    }


def _calcular_formula(protocolo: dict, parametros: dict) -> dict:
    from planejador.core.preparos import escalonar_formulacao

    recipe = next(
        (
            x
            for x in protocolo["formulacoes"]
            if x["id"] == parametros.get("formulacao_id")
        ),
        None,
    )
    if recipe is None and parametros.get("formulacao_id") != "pesquisador":
        raise EntradaInvalida("Qual formulação deseja usar?")
    texts = {}
    for key in ("fonte_formula", "procedimento_formula", "ph", "ciclo", "conservacao"):
        value = parametros.get(key, "")
        if not isinstance(value, str) or len(value) > 2000:
            raise EntradaInvalida(
                "As respostas sobre fonte e condições devem ter até 2000 caracteres."
            )
        texts[key] = value.strip()
    if recipe is None and not texts["fonte_formula"]:
        raise EntradaInvalida(
            "Qual fonte ou autoria fundamenta a formulação? Pode indicar formulação própria do pesquisador."
        )
    if recipe and (
        parametros.get("componentes", recipe["componentes"]) != recipe["componentes"]
        or parametros.get("volume_base_mL", recipe["volume_base_mL"])
        != recipe["volume_base_mL"]
    ):
        raise EntradaInvalida(
            "A formulação da fonte foi alterada. Selecione formulação do pesquisador para identificar a adaptação."
        )
    base = recipe["volume_base_mL"] if recipe else parametros.get("volume_base_mL", 0)
    ingredients = recipe["componentes"] if recipe else parametros.get("componentes", [])
    target = parametros.get("volume_alvo_mL", 0)
    scaled = escalonar_formulacao(ingredients, base, target)
    ph = recipe["ph"] if recipe else texts["ph"]
    preparation = recipe["procedimento"] if recipe else texts["procedimento_formula"]
    storage = recipe["conservacao"] if recipe else texts["conservacao"]
    pending = [
        question
        for value, question in (
            (preparation, "Qual procedimento acompanha a formulação?"),
            (ph, "Qual pH e condição de medida foram definidos?"),
            (
                texts["ciclo"],
                "Qual processo/ciclo de esterilização foi definido para este meio e esta carga?",
            ),
            (
                storage,
                "Quais condições de conservação e validade foram definidas pelo método?",
            ),
        )
        if not value
    ]
    origin = (
        f"{protocolo['fontes'][0]['id']}, p. 15"
        if recipe
        else f"Informada pelo pesquisador: {texts['fonte_formula']}; não validada pela fonte de referência do aplicativo"
    )
    return {
        "protocolo": f"{protocolo['id']} · {protocolo['name']}",
        "protocolo_id": protocolo["id"],
        "tipo_calculo": "formula",
        "pendente": False,
        "resultado": {
            "quantidade_final": target,
            "unidade_final": "mL",
            "volume_base_mL": base,
            "fator_escala": target / base,
        },
        "formula_origem": origin,
        "componentes_referencia": ingredients,
        "reagentes": scaled,
        "materiais": [],
        "equipamentos": protocolo.get("equipamentos", []),
        "solvente": "Água ou solvente permanece como componente da receita, sem converter automaticamente para q.s.p.",
        "condicoes_preparo": {
            "ph": ph,
            "procedimento": preparation,
            "ciclo_informado": texts["ciclo"],
            "conservacao": storage,
        },
        "pendencias_preparo": pending,
        "procedimento": [
            f"Conferir a formulação e sua origem: {origin}.",
            f"Escalar cada ingrediente pelo fator {target / base:.6g}, para {target:.6g} mL nominais de referência; preservar a unidade de cada componente.",
            *[
                f"Medir {x['quantidade_total']:.6g} {x['unidade']} de {x['nome']}."
                for x in scaled
            ],
            f"Procedimento da formulação: {preparation or 'pendente de resposta do pesquisador'}",
            f"pH e condição: {ph or 'pendentes'}. Processo/ciclo informado pelo pesquisador: {texts['ciclo'] or 'pendente, não presumido'}. Conservação/validade informadas: {storage or 'pendentes, não presumidas'}.",
            "Conferir o controle de qualidade e os requisitos do método antes de executar.",
        ],
        "fontes": protocolo["fontes"],
        "limites": "Escalonamento nominal, sem garantia de volume final exato após dissolução. A receita do pesquisador e as condições informadas não foram validadas automaticamente. Dados de preparo ausentes permanecem pendentes; sem validação em bancada.",
    }


def _calcular_recipientes(protocolo: dict, parametros: dict) -> dict:
    kind = parametros.get("recipiente")
    if kind not in ("placas", "tubos"):
        raise EntradaInvalida("O meio será distribuído em placas ou tubos?")
    details = {}
    for key in ("formato_recipiente", "metodo_distribuicao"):
        value = parametros.get(key, "")
        if not isinstance(value, str) or len(value) > 2000:
            raise EntradaInvalida(
                "Formato e método devem ser textos com até 2000 caracteres."
            )
        details[key] = value.strip()
    plan = _calcular_volume(protocolo, parametros)
    plan["tipo_calculo"] = "recipientes"
    plan["recipiente"] = kind
    plan["n_recipientes"] = parametros["n_unidades"]
    plan["distribuicao"] = details
    plan["pendencias_preparo"] = [
        question
        for key, question in (
            (
                "formato_recipiente",
                "Qual formato/capacidade do recipiente será utilizado?",
            ),
            (
                "metodo_distribuicao",
                "Qual método orienta o volume, preparo e distribuição do meio?",
            ),
        )
        if not details[key]
    ]
    plan["procedimento"] = [
        f"Conferir {parametros['n_unidades']} {kind}, já incluindo controles e repetições. Formato/capacidade: {details['formato_recipiente'] or 'pendente'}. Não usar capacidade nominal como dose automaticamente.",
        *plan["procedimento"][1:],
        f"Método declarado pelo pesquisador: {details['metodo_distribuicao'] or 'pendente'}. Conferir composição, preparo, temperatura/processo de distribuição, esterilidade e conservação antes de executar; não inferidos pelo cálculo de volume.",
    ]
    plan["limites"] += (
        " Um tipo de recipiente e uma dose por planejamento; grupos com doses ou meios diferentes exigem planejamentos separados. Formato, dose e condições são informados pelo pesquisador, sem dose universal para placas ou tubos. Não calcula massa de pó nem valida o método declarado."
    )
    return plan


def _calcular_volume(protocolo: dict, parametros: dict) -> dict:
    from planejador.core.calculos import escalonar_quantidade

    unit = parametros.get("unidade_volume")
    if not isinstance(unit, str) or unit not in {"µL", "mL", "L"}:
        raise EntradaInvalida("Qual é a unidade do volume: µL, mL ou L?")
    n = parametros.get("n_unidades", 0)
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 1000000:
        raise EntradaInvalida(
            "Quantas unidades receberão o volume? Informe inteiro de 1 a 1000000, incluindo controles e repetições já contados."
        )
    v = parametros.get("volume_unitario", 0)
    excess = parametros.get("excesso_percentual", 0)
    base = escalonar_quantidade(v, n, 0)
    total = escalonar_quantidade(v, n, excess)
    extra = total - base
    name = parametros.get("soluto", "").strip() or "Material não identificado"
    return {
        "protocolo": f"{protocolo['id']} · {protocolo['name']}",
        "protocolo_id": protocolo["id"],
        "tipo_calculo": "volume",
        "pendente": False,
        "resultado": {
            "quantidade_reagente": total,
            "unidade_reagente": unit,
            "quantidade_final": total,
            "unidade_final": unit,
            "volume_sem_excedente": base,
            "volume_excedente": extra,
        },
        "reagentes": [{"nome": name, "quantidade_total": total, "unidade": unit}],
        "materiais": [],
        "equipamentos": protocolo.get("equipamentos", []),
        "solvente": "Não se aplica ao dimensionamento de volume; composição definida pelo método.",
        "procedimento": [
            "Conferir volume por unidade e contar todas as unidades que receberão esse volume, incluindo controles e repetições pertinentes; não os contar novamente.",
            f"Volume base: {v:.6g} {unit} × {n} unidades = {base:.6g} {unit}.",
            f"Excedente escolhido pelo pesquisador: {excess:.6g}% do volume base = {extra:.6g} {unit}; preparar {total:.6g} {unit} de {name}.",
            "Selecionar instrumentos e recipientes compatíveis com o volume, composição e condições do método. Distribuir o volume por unidade, sem aumentar a dose para consumir a reserva.",
        ],
        "fontes": protocolo["fontes"],
        "limites": "Excedente é acréscimo sobre a base, não compensação automática por fração perdida do total. Não define composição, concentração, margem universal ou estabilidade; não demonstra execução em bancada.",
    }


def _calcular_seriada(protocolo: dict, parametros: dict) -> dict:
    import math

    from planejador.core.calculos import diluicao_seriada, preparar_diluicao

    unit = parametros.get("unidade_concentracao")
    if not isinstance(unit, str) or unit not in {
        "mg/mL",
        "µg/mL",
        "g/L",
        "mol/L",
        "mmol/L",
        "U/mL",
        "% m/v",
        "% v/v",
    }:
        raise EntradaInvalida(
            "Escolha uma unidade por volume para toda a série; % m/m não se aplica."
        )
    n = parametros.get("n_diluicoes")
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 100:
        raise EntradaInvalida(
            "Quantas diluições deseja preparar? Informe inteiro de 1 a 100, sem contar o estoque."
        )
    equalize = parametros.get("igualar_ultimo", False)
    if not isinstance(equalize, bool):
        raise EntradaInvalida(
            "Informe se deseja retirar uma alíquota do último recipiente para igualar os volumes."
        )
    c0 = parametros.get("concentracao_inicial", 0)
    factor = parametros.get("fator", 0)
    concentrations = diluicao_seriada(c0, factor, n + 1)[1:]
    if unit == "% v/v" and c0 > 100:
        raise EntradaInvalida(
            "Concentração inicial em % v/v não pode ultrapassar 100%."
        )
    volume = parametros.get("quantidade_final", 0)
    transfer = preparar_diluicao(c0, concentrations[0], volume)
    a = transfer.volume_alicota
    nominal = transfer.volume_diluente
    if not math.isfinite(nominal * n) or not math.isfinite(volume * n):
        raise EntradaInvalida("Os volumes totais excedem a faixa numérica suportada.")
    etapas = []
    for k, c in enumerate(concentrations, 1):
        cumulative = c0 / c
        if not math.isfinite(cumulative):
            raise EntradaInvalida(
                "O fator acumulado excede a faixa numérica suportada."
            )
        etapas.append(
            {
                "etapa": k,
                "concentracao": c,
                "fator_acumulado": cumulative,
                "volume_transferido_mL": a,
                "volume_diluente_nominal_mL": nominal,
                "volume_preparado_mL": volume,
                "volume_restante_mL": nominal if k < n or equalize else volume,
            }
        )
    stock = parametros.get("soluto", "").strip() or "Estoque não identificado"
    diluent = parametros.get("solvente", "").strip() or "Diluente não informado"
    return {
        "protocolo": f"{protocolo['id']} · {protocolo['name']}",
        "protocolo_id": protocolo["id"],
        "tipo_calculo": "seriada",
        "pendente": False,
        "unidade_concentracao": unit,
        "observacao_diluicao": f"{n} diluições, {volume:.6g} mL preparados por etapa antes de retirar a próxima alíquota. "
        + (
            "Volumes finais igualados por retirada no último recipiente."
            if equalize
            else "Último recipiente mantém volume completo."
        ),
        "resultado": {
            "quantidade_reagente": a,
            "unidade_reagente": "mL",
            "quantidade_final": volume,
            "unidade_final": "mL",
            "fator_diluicao": factor,
            "diluente_total_nominal_mL": nominal * n,
        },
        "etapas": etapas,
        "igualar_ultimo": equalize,
        "reagentes": [{"nome": stock, "quantidade_total": a, "unidade": "mL"}],
        "materiais": [],
        "equipamentos": protocolo.get("equipamentos", []),
        "solvente": f"{diluent}: {nominal:.6g} mL nominais por etapa; {nominal * n:.6g} mL nominais no total",
        "procedimento": [
            "Conferir estoque, diluente, compatibilidade, unidades e faixa/tolerância do instrumento. Volumes nominais pressupõem mistura compatível; seguir aferição e condições do método.",
            f"Identificar {n} recipientes, sem contar o estoque. Cada etapa terá {volume:.6g} mL antes da transferência ao seguinte.",
            *[
                f"Etapa {s['etapa']}: transferir {a:.6g} mL {'do estoque' if s['etapa'] == 1 else 'da etapa anterior homogeneizada'} para diluente conforme o método, até {volume:.6g} mL preparados; concentração {s['concentracao']:.6g} {unit}. Homogeneizar antes da próxima transferência; usar pipeta/ponteira adequada e nova a cada transferência. Restam {s['volume_restante_mL']:.6g} mL após as retiradas planejadas."
                for s in etapas
            ],
            (
                f"Retirar também {a:.6g} mL do último recipiente, conforme decisão do pesquisador e destinação definida pelo método, para igualar volumes."
                if equalize
                else "Manter o volume completo do último recipiente; não foi planejada retirada final. Os intermediários já perderam uma alíquota para a etapa seguinte."
            ),
        ],
        "fontes": protocolo["fontes"],
        "limites": "Série volumétrica de fator constante, volumes nominais e soluto/atividade conservados. Não calcula preparo de amostra sólida, contagem de colônias, cultivo, estabilidade ou tolerância de equipamento. Sem validação em bancada.",
    }
