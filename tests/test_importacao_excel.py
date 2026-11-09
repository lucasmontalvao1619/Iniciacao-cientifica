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
