"""Exportações portáveis de observações e análise, com contexto rastreável."""

import csv
import json
from pathlib import Path


def exportar_resultados(destino, payload, *, resumo_csv=False):
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
            for row in stats if resumo_csv else rows:
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
        trace_rows = [["Campo", "Informação"]]
        for key, value in metadata.items():
            serialized = json.dumps(value, ensure_ascii=False, allow_nan=False)
            for offset in range(0, max(1, len(serialized)), 30000):
                trace_rows.append(
                    [
                        key if offset == 0 else f"{key} continuação {offset // 30000}",
                        serialized[offset : offset + 30000],
                    ]
                )
        for name, data in [
            ("Medições", rows),
            ("Resumo", stats),
            ("Rastreabilidade", trace_rows),
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
        plan = payload.get("planejamento") or {}
        document.add_heading("Planejamento utilizado", 1)
        for key, value in payload.get("parametros_planejados", {}).items():
            document.add_paragraph(f"{key.replace('_', ' ').capitalize()}: {value}")
        if plan.get("resultado"):
            for key, value in plan["resultado"].items():
                document.add_paragraph(f"{key.replace('_', ' ').capitalize()}: {value}")
        if plan.get("procedimento"):
            document.add_heading("Procedimento planejado", 1)
            for step in plan["procedimento"]:
                document.add_paragraph(str(step), style="List Number")
        document.add_heading("Fontes do protocolo", 1)
        for source in plan.get("fontes", []):
            pages = ", ".join(map(str, source.get("paginas", [])))
            document.add_paragraph(
                f"{source.get('title', source.get('id', 'Fonte'))}. {source.get('organization', '')}, {source.get('year', '')}. Páginas: {pages}."
            )
            document.add_paragraph(source.get("url", ""))
            document.add_paragraph(
                f"Consulta registrada: {source.get('consultado_em', 'Não informada')}"
            )
        document.add_heading("Condições da análise e rastreabilidade", 1)
        document.add_paragraph(
            "Desenho informado: "
            + str(payload.get("desenho_informado", "Não informado"))
        )
        document.add_paragraph(
            "Pressupostos declarados conferidos: "
            + ("Sim" if payload.get("pressupostos_conferidos") else "Não")
        )
        document.add_paragraph(
            "Nível de significância: " + str(payload.get("alpha", 0.05))
        )
        document.add_paragraph(
            "Registro do planejamento: "
            + str(context.get("registro_id", "Não informado"))
        )
        document.add_paragraph(
            "Identificador do conteúdo planejado: "
            + str(context.get("planejamento_sha256", "Não informado"))
        )
        imported = payload.get("importacao")
        if imported:
            document.add_paragraph(
                f"Arquivo importado: {imported.get('arquivo')}; aba: {imported.get('aba')}; SHA-256: {imported.get('sha256')}"
            )
        if payload.get("coleta_planejada"):
            document.add_heading("Organização da coleta", 1)
            for unit in payload["coleta_planejada"]["unidades"]:
                document.add_paragraph(
                    f"{unit['amostra']} · {unit['grupo']} · repetição {unit['repeticao']} · placa {unit.get('placa')} · poço {unit.get('poco')}"
                )
        document.save(path)
    else:
        raise ValueError("Escolha Excel (.xlsx), CSV (.csv) ou relatório Word (.docx).")
