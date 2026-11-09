import pytest

from planejador.services.importacao_excel import read_workbook, recognize


@pytest.mark.parametrize(
    "rows,expected",
    [
        (
            [["Controle", "Tratamento"], [2, 3], [4, 5], [6, 7]],
            {"Controle": [2, 4, 6], "Tratamento": [3, 5, 7]},
        ),
        (
            [["Grupo", "Medição 1", "Medição 2"], ["A", "1,5", 2], ["B", 3, 4]],
            {"A": [1.5, 2], "B": [3, 4]},
        ),
        (
            [
                ["Grupo", "Amostra", "Valor"],
                ["A", "x", 2],
                ["B", "y", 4],
                ["A", "z", 6],
            ],
            {"A": [2, 6], "B": [4]},
        ),
    ],
)
def test_formats(rows, expected):
    assert recognize(rows)[1] == expected


@pytest.mark.parametrize(
    "rows",
    [
        [["Grupo", "Valor"], ["A", None]],
        [["A", "A"], [1, 2]],
        [["A"], ["nan"]],
        [[1, 2], [3, 4]],
        [["Grupo", "Medição 1"], ["A", True]],
    ],
)
def test_invalid_data_is_not_silently_imported(rows):
    with pytest.raises(ValueError):
        recognize(rows)


def test_workbook_formula_and_multiple_sheets(tmp_path):
    from openpyxl import Workbook

    path = tmp_path / "dados.xlsx"
    book = Workbook()
    book.active.append(["A"])
    book.active.append([2])
    book.create_sheet("Outra").append(["B"])
    book.save(path)
    assert len(read_workbook(path)) == 2
    book.active.append(["=1+1"])
    book.save(path)
    with pytest.raises(ValueError, match="fórmula"):
        read_workbook(path)


def test_numeric_identifiers_require_column_selection():
    rows = [["Amostra", "Controle", "Tratamento"], [1, 2, 3], [2, 4, 5]]
    with pytest.raises(ValueError, match="identificadores"):
        recognize(rows)
    assert recognize(rows, "columns", columns=[1, 2])[1] == {
        "Controle": [2, 4],
        "Tratamento": [3, 5],
    }


def test_explicit_header_and_long_mapping():
    rows = [
        ["Título"],
        [],
        ["Código", "Condição experimental", "Leitura OD"],
        ["x", "A", 0.2],
        ["y", "B", "0,3"],
    ]
    assert recognize(rows, "long", header_row=2, group_column=1, value_column=2)[1] == {
        "A": [0.2],
        "B": [0.3],
    }
    with pytest.raises(ValueError, match="distintas"):
        recognize(rows, "long", header_row=2, group_column=2, value_column=2)
