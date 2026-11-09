"""Exportações portáveis de observações e análise, com contexto rastreável."""

import csv
import json
from pathlib import Path


def exportar_resultados(destino, payload):
    path = Path(destino)
    groups = payload["medicoes"]
    summaries = payload["analise"]["resumos"]
    rows = [["Grupo", "Medição", "Valor", "Unidade"]]
    rows += [
        [name, index, value, payload["unidade"]]
        for name, values in groups.items()
        for index, value in enumerate(values, 1)
    ]
    stats = [["Grupo", "n", "Média", "Desvio padrão", "Variância"]]
    stats += [
        [name, s["n"], s["media"], s["desvio_padrao"], s["variancia"]]
        for name, s in summaries.items()
    ]
    metadata = {k: v for k, v in payload.items() if k != "medicoes"}
    json.dumps(payload, allow_nan=False)
    if path.suffix.lower() == ".csv":
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, delimiter=";")
            for row in rows:
                writer.writerow(
                    [
                        ("'" + v if v.startswith(("=", "+", "-", "@")) else v)
                        if isinstance(v, str)
                        else str(v).replace(".", ",")
                        for v in row
                    ]
                )
    elif path.suffix.lower() == ".xlsx":
        from openpyxl import Workbook

        book = Workbook()
        book.remove(book.active)
        for name, data in [
            ("Medições", rows),
            ("Resumo", stats),
            (
                "Rastreabilidade",
                [["Campo", "Informação"]]
                + [
                    [k, json.dumps(v, ensure_ascii=False, allow_nan=False)]
                    for k, v in metadata.items()
                ],
            ),
        ]:
            sheet = book.create_sheet(name)
            for row in data:
                sheet.append(row)
            for row in sheet:
                for cell in row:
                    if isinstance(cell.value, str):
                        cell.data_type = "s"
            sheet.freeze_panes = "A2"
            for column in sheet.columns:
                sheet.column_dimensions[column[0].column_letter].width = 24
        book.save(path)
        book.close()
    elif path.suffix.lower() == ".docx":
        from docx import Document

        document = Document()
        document.add_heading("Relatório do experimento", 0)
        context = payload["analise"].get("experimento", {})
        document.add_paragraph(context.get("titulo", "Experimento"))
        document.add_paragraph(
            "Protocolo: " + context.get("protocolo", "Não informado")
        )
        document.add_paragraph("Grandeza/unidade: " + payload["unidade"])
        document.add_heading("Resumo estatístico", 1)
        table = document.add_table(rows=0, cols=5)
        table.style = "Light Shading Accent 1"
        for row in stats:
            for cell, value in zip(table.add_row().cells, row, strict=True):
                cell.text = str(value)
        test = payload["analise"].get("teste_t") or payload["analise"].get("anova")
        document.add_paragraph(
            "Comparação: " + json.dumps(test, ensure_ascii=False)
            if test
            else "Comparação entre grupos não solicitada."
        )
        document.add_heading("Dados observados", 1)
        table = document.add_table(rows=0, cols=4)
        table.style = "Light Shading Accent 1"
        for row in rows:
            for cell, value in zip(table.add_row().cells, row, strict=True):
                cell.text = str(value)
        document.add_heading("Rastreabilidade e opções informadas", 1)
        document.add_paragraph(
            json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False)
        )
        document.save(path)
    else:
        raise ValueError("Escolha Excel (.xlsx), CSV (.csv) ou relatório Word (.docx).")
