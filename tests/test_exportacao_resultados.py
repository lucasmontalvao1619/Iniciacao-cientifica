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


def test_report_includes_plan_parameters_and_sources(tmp_path):
    payload = {
        "unidade": "mg/mL",
        "medicoes": {"A": [2, 4, 6]},
        "analise": {
            "resumos": {"A": {"n": 3, "media": 4, "desvio_padrao": 2, "variancia": 4}},
            "experimento": {"titulo": "Experimento", "protocolo": "PREP-003"},
        },
        "planejamento": {
            "resultado": {"massa": 2.5},
            "procedimento": ["Conferir o procedimento do método."],
            "fontes": [
                {
                    "title": "Fonte institucional",
                    "organization": "Fiocruz",
                    "year": 2009,
                    "paginas": [227],
                    "url": "https://www.arca.fiocruz.br/",
                    "consultado_em": "2026-11-08",
                }
            ],
        },
        "parametros_planejados": {"quantidade_final": 250},
    }
    path = tmp_path / "relatorio.docx"
    exportar_resultados(path, payload)
    text = "\n".join(p.text for p in Document(path).paragraphs)
    assert "Quantidade final: 250" in text
    assert "Fonte institucional" in text and "227" in text
    assert "Conferir o procedimento" in text


def test_report_explains_test_without_code_and_formats_numbers(tmp_path):
    from planejador.services import analisar_grupos

    groups = {"Controle": [2, 4, 6], "Tratamento": [3, 5, 7]}
    payload = {
        "unidade": "mg/mL",
        "medicoes": groups,
        "analise": analisar_grupos(groups),
        "planejamento": {"resultado": {"massa_g": 0.15000000000000002}},
    }
    path = tmp_path / "relatorio.docx"
    exportar_resultados(path, payload)
    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Teste t de Student: t =" in text
    assert "Isso não demonstra equivalência" in text
    assert '"estatistica_t"' not in text
    assert "Massa g: 0,15" in text
    assert all(table.rows[0]._tr.xpath("./w:trPr/w:tblHeader") for table in doc.tables)


def test_summary_csv_is_distinct_from_observations(tmp_path):
    payload = {
        "unidade": "mg/mL",
        "medicoes": {"=A": [2, 4, 6]},
        "analise": {
            "resumos": {"=A": {"n": 3, "media": 4, "desvio_padrao": 2, "variancia": 4}}
        },
    }
    path = tmp_path / "resumo.csv"
    exportar_resultados(path, payload, resumo_csv=True)
    with path.open(encoding="utf-8-sig") as stream:
        rows = list(csv.reader(stream, delimiter=";"))
    assert rows[0] == ["Grupo", "n", "Média", "Desvio padrão", "Variância"]
    assert rows[1] == ["'=A", "3", "4", "2", "4"]
