"""Leitura de medições Excel sem executar fórmulas nem modificar o arquivo."""

import math
import unicodedata
from pathlib import Path


def normalized(value):
    return "".join(
        c
        for c in unicodedata.normalize("NFD", str(value).strip().lower())
        if not unicodedata.combining(c)
    )


def numeric(value, location):
    if isinstance(value, bool):
        raise ValueError(f"{location}: valor lógico não é uma medição.")
    try:
        result = float(str(value).strip().replace(",", "."))
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{location}: medição inválida ({value}).") from exc
    if not math.isfinite(result):
        raise ValueError(f"{location}: informe um número finito.")
    return result


def read_workbook(path):
    from openpyxl import load_workbook

    path = Path(path)
    if path.suffix.lower() != ".xlsx":
        raise ValueError(
            "Escolha um arquivo .xlsx. Salve planilhas antigas nesse formato no Excel."
        )
    if path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError("O arquivo deve ter até 20 MB.")
    book = load_workbook(path, read_only=True, data_only=False, keep_links=False)
    sheets = {}
    try:
        total = 0
        for sheet in book:
            rows = []
            for row in sheet.iter_rows():
                values = []
                for cell in row:
                    total += 1
                    if total > 100000:
                        raise ValueError(
                            "A planilha excede 100.000 células. Importe uma seleção menor."
                        )
                    if cell.data_type == "f":
                        raise ValueError(
                            f"{sheet.title}!{cell.coordinate}: fórmula encontrada. Exporte as medições como valores antes de importar."
                        )
                    values.append(cell.value)
                while values and values[-1] is None:
                    values.pop()
                rows.append(values)
            if any(any(v is not None for v in row) for row in rows):
                sheets[sheet.title] = rows
    finally:
        book.close()
    if not sheets:
        raise ValueError("Nenhuma aba contém dados.")
    return sheets


def recognize(rows, mode="auto"):
    """Aceita grupos em colunas, grupos em linhas e formato longo grupo/valor."""
    start = next(
        (i for i, row in enumerate(rows) if any(v is not None for v in row)), None
    )
    if start is None:
        raise ValueError("A aba está vazia.")
    header = rows[start]
    names = [normalized(v) for v in header]
    group_col = next(
        (i for i, h in enumerate(names) if h in {"grupo", "tratamento", "condicao"}),
        None,
    )
    value_col = next(
        (i for i, h in enumerate(names) if h in {"valor", "medicao", "resultado"}), None
    )
    if mode == "auto":
        if group_col is not None and value_col is not None:
            mode = "long"
        elif (
            group_col == 0
            and len(header) > 1
            and all(
                h.startswith(("medicao", "replica", "repeticao")) for h in names[1:]
            )
        ):
            mode = "rows"
        elif (
            header
            and all(isinstance(v, str) and v.strip() for v in header)
            and (group_col is None or "grupo" not in names)
        ):
            mode = "columns"
        else:
            raise ValueError(
                "Formato ambíguo. Escolha a organização das medições na prévia."
            )
    groups = {}
    if mode == "columns":
        labels = [str(v).strip() if v is not None else "" for v in header]
        if not all(labels) or len({v.casefold() for v in labels}) != len(labels):
            raise ValueError("Cada coluna precisa de um nome de grupo único.")
        groups = {name: [] for name in labels}
    for index, row in enumerate(rows[start + 1 :], start + 2):
        if not any(v is not None and str(v).strip() for v in row):
            continue
        if mode == "columns":
            if len(row) > len(header):
                raise ValueError(f"Linha {index}: existem valores sem cabeçalho.")
            for col, value in enumerate(row):
                if value is not None and str(value).strip():
                    groups[labels[col]].append(
                        numeric(value, f"Linha {index}, coluna {col + 1}")
                    )
        elif mode in {"rows", "long"}:
            gc, vc = (group_col, value_col) if mode == "long" else (0, None)
            if gc is None or (mode == "long" and vc is None):
                raise ValueError(
                    "Formato longo exige cabeçalhos Grupo e Valor (ou Medição/Resultado)."
                )
            name = str(row[gc]).strip() if gc < len(row) and row[gc] is not None else ""
            if not name:
                raise ValueError(f"Linha {index}: grupo ausente.")
            if mode == "rows" and name in groups:
                raise ValueError(
                    f"Linha {index}: grupo repetido. Escolha formato longo se houver uma linha por observação."
                )
            values = [row[vc] if vc < len(row) else None] if mode == "long" else row[1:]
            if mode == "long" and (values[0] is None or not str(values[0]).strip()):
                raise ValueError(f"Linha {index}: medição ausente.")
            groups.setdefault(name, []).extend(
                numeric(v, f"Linha {index}")
                for v in values
                if v is not None and str(v).strip()
            )
        else:
            raise ValueError("Formato não reconhecido.")
    if not groups or any(not values for values in groups.values()):
        raise ValueError("Há grupos sem medições. Confira os cabeçalhos e os dados.")
    return mode, groups
