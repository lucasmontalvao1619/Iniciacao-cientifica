import pytest

from planejador.services.coleta import exportar_modelo, organizar_coleta
from planejador.services.importacao_excel import read_workbook, recognize


def test_collection_and_excel_roundtrip(tmp_path):
    from openpyxl import load_workbook

    units = organizar_coleta(["Controle", "Tratamento"], 3)
    assert len(units) == 6 and len({u["amostra"] for u in units}) == 6
    path = tmp_path / "coleta.xlsx"
    exportar_modelo(path, units, {"protocolo_id": "PREP-003"}, "mg/mL")
    book = load_workbook(path)
    for row in range(2, 8):
        assert book["Medições"].cell(row, 7).value is None
        book["Medições"].cell(row, 7, row - 1)
    book.save(path)
    book.close()
    assert recognize(read_workbook(path)["Medições"])[1] == {
        "Controle": [1, 2, 3],
        "Tratamento": [4, 5, 6],
    }


def test_plate_and_validation():
    units = organizar_coleta(["A"], 100, microplaca=True)
    assert units[0]["poco"] == "A1" and units[95]["poco"] == "H12"
    assert units[96]["placa"] == 2 and units[96]["poco"] == "A1"
    with pytest.raises(ValueError):
        organizar_coleta(["A", "a"], 3)
    with pytest.raises(ValueError):
        organizar_coleta(["A"], 0)


def test_manifest_binds_samples_positions_and_plan(tmp_path):
    from openpyxl import load_workbook

    from planejador.services.coleta import conferir_coleta

    units = organizar_coleta(["Controle", "Tratamento"], 2, microplaca=True)
    collection = {"unidades": units, "unidade": "mg/mL"}
    context = {"registro_id": "experimento-1", "planejamento_sha256": "plano-1"}
    path = tmp_path / "modelo.xlsx"
    exportar_modelo(path, units, {**context, "coleta": collection}, "mg/mL")
    book = load_workbook(path)
    for i in range(2, 6):
        book["Medições"].cell(i, 7, i)
    book.save(path)
    book.close()
    sheets = read_workbook(path)
    assert conferir_coleta(sheets, context) == collection
    with pytest.raises(ValueError, match="outro planejamento"):
        conferir_coleta(sheets, {**context, "registro_id": "outro"})
    sheets["Medições"][2][1] = sheets["Medições"][1][1]
    with pytest.raises(ValueError, match="repetido"):
        conferir_coleta(sheets, context)


def test_large_manifest_is_not_truncated_by_excel(tmp_path):
    from openpyxl import load_workbook

    from planejador.services.coleta import conferir_coleta

    units = organizar_coleta([f"Grupo{i}" for i in range(10)], 100)
    collection = {"unidades": units, "unidade": "mg/mL"}
    context = {"registro_id": "r", "planejamento_sha256": "p"}
    path = tmp_path / "grande.xlsx"
    exportar_modelo(path, units, {**context, "coleta": collection}, "mg/mL")
    book = load_workbook(path)
    for row in range(2, 1002):
        book["Medições"].cell(row, 7, row)
    book.save(path)
    book.close()
    assert conferir_coleta(read_workbook(path), context) == collection
