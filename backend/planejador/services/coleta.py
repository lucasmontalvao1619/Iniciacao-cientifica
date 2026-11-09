"""Organização de coleta comum a preparos e ensaios; não fabrica observações."""

import json
from pathlib import Path


def organizar_coleta(grupos, repeticoes, *, linhas=8, colunas=12, microplaca=False):
    if (
        isinstance(repeticoes, bool)
        or not isinstance(repeticoes, int)
        or not 1 <= repeticoes <= 100
    ):
        raise ValueError("Informe entre 1 e 100 repetições por grupo.")
    names = [str(g).strip() for g in grupos]
    if not names or any(not n or len(n) > 160 for n in names):
        raise ValueError("Informe nomes de grupos com até 160 caracteres.")
    if len({n.casefold() for n in names}) != len(names):
        raise ValueError("Cada grupo precisa de um nome único.")
    if not 1 <= linhas <= 26 or not 1 <= colunas <= 48:
        raise ValueError("Geometria de microplaca inválida.")
    if len(names) * repeticoes > 10000:
        raise ValueError("Organize até 10.000 unidades por experimento.")
    capacity = linhas * colunas
    units = []
    for name in names:
        for replica in range(1, repeticoes + 1):
            i = len(units)
            units.append(
                {
                    "amostra": f"U{i + 1:05}",
                    "grupo": name,
                    "repeticao": replica,
                    "placa": i // capacity + 1 if microplaca else None,
                    "poco": f"{chr(65 + (i % capacity) // colunas)}{i % colunas + 1}"
                    if microplaca
                    else None,
                }
            )
    return units


def exportar_modelo(destino, unidades, contexto, unidade):
    from openpyxl import Workbook

    if not unidade.strip():
        raise ValueError("Informe a grandeza/unidade a medir.")
    book = Workbook()
    sheet = book.active
    sheet.title = "Medições"
    sheet.append(["Grupo", "Amostra", "Repetição", "Placa", "Poço", "Unidade", "Valor"])
    for u in unidades:
        sheet.append(
            [
                u["grupo"],
                u["amostra"],
                u["repeticao"],
                u["placa"],
                u["poco"],
                unidade,
                None,
            ]
        )
    for row in sheet:
        for cell in row:
            if isinstance(cell.value, str):
                cell.data_type = "s"
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for col in sheet.columns:
        sheet.column_dimensions[col[0].column_letter].width = 22
    metadata = book.create_sheet("Planejamento")
    metadata.append(
        ["Contexto", json.dumps(contexto, ensure_ascii=False, allow_nan=False)]
    )
    metadata.append(
        ["Medições", "Preencher somente observações reais na coluna Valor."]
    )
    book.save(Path(destino))
    book.close()


def conferir_coleta(sheets, contexto):
    """Confere modelo gerado; planilha externa sem manifesto segue para a prévia."""
    if "Planejamento" not in sheets:
        return None
    metadata = {str(row[0]): row[1] for row in sheets["Planejamento"] if len(row) >= 2}
    if "Contexto" not in metadata:
        return None
    try:
        saved = json.loads(metadata["Contexto"])
    except (TypeError, ValueError) as exc:
        raise ValueError("O contexto do modelo de coleta está inválido.") from exc
    for field in ("registro_id", "planejamento_sha256"):
        if saved.get(field) is not None and saved.get(field) != contexto.get(field):
            raise ValueError(
                "Esta planilha pertence a outro planejamento. Abra a coleta correspondente."
            )
    collection = saved.get("coleta")
    if not collection:
        return None
    if "Medições" not in sheets:
        raise ValueError("A aba Medições do modelo está ausente.")
    rows = sheets["Medições"]
    required = ["Grupo", "Amostra", "Repetição", "Placa", "Poço", "Unidade", "Valor"]
    if not rows or rows[0] != required:
        raise ValueError("Os cabeçalhos do modelo foram alterados.")
    expected = {u["amostra"]: u for u in collection["unidades"]}
    seen = set()
    for number, row in enumerate(rows[1:], 2):
        if not any(v is not None for v in row):
            continue
        if len(row) < 7 or row[6] is None:
            raise ValueError(
                f"Linha {number}: medição pendente; preencha a coleta antes de importar."
            )
        name, identity, repetition, plate, well, unit, value = row
        if identity not in expected or identity in seen:
            raise ValueError(
                f"Linha {number}: identificador ausente, desconhecido ou repetido."
            )
        seen.add(identity)
        planned = expected[identity]
        if (name, repetition, plate, well) != (
            planned["grupo"],
            planned["repeticao"],
            planned["placa"],
            planned["poco"],
        ):
            raise ValueError(
                f"Linha {number}: grupo, repetição ou posição diverge do planejamento."
            )
        if unit != collection["unidade"]:
            raise ValueError(f"Linha {number}: unidade diferente da coleta planejada.")
    if seen != set(expected):
        raise ValueError("Há amostras planejadas ausentes na planilha.")
    return collection
