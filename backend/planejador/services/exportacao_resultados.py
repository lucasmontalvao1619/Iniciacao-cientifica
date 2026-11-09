"""Exportações portáveis de observações e análise, com contexto rastreável."""

import csv
import json
from datetime import UTC, datetime
from pathlib import Path


def _texto(value):
    if value is None:
        return "Não informado"
    if isinstance(value, bool):
        return "Sim" if value else "Não"
    if isinstance(value, float):
        return format(value, ".8g").replace(".", ",")
    if isinstance(value, dict):
        return "; ".join(
            f"{k.replace('_', ' ')}: {_texto(v)}" for k, v in value.items()
        )
    if isinstance(value, list):
        return "; ".join(map(_texto, value))
    return str(value)


def _tabela(document, rows):
    from docx.oxml import OxmlElement

    table = document.add_table(rows=0, cols=len(rows[0]))
    table.style = "Light Shading Accent 1"
    for values in rows:
        row = table.add_row()
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for cell, value in zip(row.cells, values, strict=True):
            cell.text = _texto(value)
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    return table


def exportar_resultados(destino, payload, *, resumo_csv=False, grafico=None):
    from planejador.services.arquivos import gravacao_atomica

    with gravacao_atomica(destino) as temporary:
        _exportar_resultados(temporary, payload, resumo_csv=resumo_csv, grafico=grafico)


def _exportar_resultados(destino, payload, *, resumo_csv=False, grafico=None):
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
        from docx.shared import Inches, Pt, RGBColor

        document = Document()
        for name in ("Normal", "Title", "Heading 1", "Heading 2"):
            style = document.styles[name]
            style.font.name = "Calibri"
            style.font.color.rgb = RGBColor(0, 0, 0)
            borders = style.element.xpath("./w:pPr/w:pBdr")
            for border in borders:
                border.getparent().remove(border)
        document.styles["Normal"].font.size = Pt(10)
        document.styles["Normal"].paragraph_format.space_after = Pt(6)
        document.styles["Title"].font.size = Pt(24)
        document.add_heading("Relatório do experimento", 0)
        context = payload["analise"].get("experimento", {})
        document.add_paragraph(context.get("titulo", "Experimento"))
        document.add_paragraph(
            "Protocolo: " + context.get("protocolo", "Não informado")
        )
        document.add_paragraph("Grandeza/unidade: " + payload["unidade"])
        from planejador import __version__

        document.add_paragraph(
            f"Aplicativo {__version__} · Exportado em {datetime.now(UTC).isoformat(timespec='seconds')}"
        )
        document.add_heading("Resumo estatístico", 1)
        _tabela(document, stats)
        document.add_paragraph(
            "Desvio padrão e variância amostrais; n é a quantidade de observações informadas em cada grupo."
        )
        test = payload["analise"].get("teste_t") or payload["analise"].get("anova")
        if test:
            is_t = bool(payload["analise"].get("teste_t"))
            name = (
                ("Teste t de Welch" if test.get("welch") else "Teste t de Student")
                if is_t
                else "ANOVA de uma via"
            )
            statistic = test["estatistica_t" if is_t else "estatistica_f"]
            document.add_paragraph(
                f"{name}: {'t' if is_t else 'F'} = {_texto(statistic)}; p = {_texto(test['valor_p'])}; α = {_texto(test['alpha'])}."
            )
            if is_t:
                document.add_paragraph(
                    f"Graus de liberdade: {_texto(test['graus_liberdade'])}."
                )
            else:
                document.add_paragraph(
                    "A ANOVA avalia diferença global entre médias; não identifica quais pares diferem."
                )
            document.add_paragraph(
                "Há evidência estatística de diferença entre as médias no nível informado."
                if test["significativo"]
                else "Não houve evidência estatística suficiente de diferença entre as médias no nível informado. Isso não demonstra equivalência."
            )
            document.add_paragraph(
                "A interpretação depende do desenho experimental e dos pressupostos declarados pelo pesquisador. Significância estatística não mede relevância prática."
            )
        else:
            document.add_paragraph("Comparação entre grupos não solicitada.")
        if grafico is not None:
            document.add_heading("Gráfico das observações", 1)
            for image in grafico if isinstance(grafico, list) else [grafico]:
                document.add_picture(image, width=Inches(6))
            document.add_paragraph(
                "Pontos representam observações; o marcador central e as barras representam média e desvio padrão amostral."
            )
        document.add_heading("Dados observados", 1)
        _tabela(document, rows)
        plan = payload.get("planejamento") or {}
        document.add_heading("Planejamento utilizado", 1)
        for key, value in payload.get("parametros_planejados", {}).items():
            document.add_paragraph(
                f"{key.replace('_', ' ').capitalize()}: {_texto(value)}"
            )
        if plan.get("resultado"):
            for key, value in plan["resultado"].items():
                document.add_paragraph(
                    f"{key.replace('_', ' ').capitalize()}: {_texto(value)}"
                )
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
            collection = payload["coleta_planejada"]
            document.add_paragraph(
                "Tipo de repetição: " + _texto(collection.get("tipo_repeticao"))
            )
            _tabela(
                document,
                [["Amostra", "Grupo", "Repetição", "Placa", "Poço"]]
                + [
                    [
                        u["amostra"],
                        u["grupo"],
                        u["repeticao"],
                        u.get("placa"),
                        u.get("poco"),
                    ]
                    for u in collection["unidades"]
                ],
            )
        document.save(path)
    else:
        raise ValueError("Escolha Excel (.xlsx), CSV (.csv) ou relatório Word (.docx).")
