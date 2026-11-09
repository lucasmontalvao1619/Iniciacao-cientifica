import csv

from docx import Document
from openpyxl import load_workbook

from planejador.services.exportacao_resultados import exportar_resultados


def test_exports_keep_observations_and_summary(tmp_path):
    payload = {
        "unidade": "mg/mL",
        "medicoes": {"A": [2, 4, 6]},
        "analise": {
            "resumos": {"A": {"n": 3, "media": 4, "desvio_padrao": 2, "variancia": 4}},
            "experimento": {"titulo": "Teste", "protocolo": "PREP-003"},
        },
        "estado": "analisado",
    }
    for extension in ("xlsx", "csv", "docx"):
        path = tmp_path / f"dados.{extension}"
        exportar_resultados(path, payload)
        assert path.stat().st_size > 10
    book = load_workbook(tmp_path / "dados.xlsx", read_only=True)
    assert list(book["Medições"].values)[1] == ("A", 1, 2, "mg/mL")
    assert list(book["Resumo"].values)[1] == ("A", 3, 4, 2, 4)
    book.close()
    with (tmp_path / "dados.csv").open(encoding="utf-8-sig") as stream:
        assert len(list(csv.reader(stream, delimiter=";"))) == 4
    doc = Document(tmp_path / "dados.docx")
    assert doc.tables[0].cell(1, 2).text == "4"
