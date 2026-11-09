"""Verificação do executável no CI, com dados descartáveis e sem janelas."""

import json
import os
import tempfile
import time
import traceback
from pathlib import Path


def verify(report_path):
    report = {"ok": False}
    try:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        with tempfile.TemporaryDirectory(prefix="planejador-check-") as directory:
            os.environ["PLANEJADOR_DATA_DIR"] = directory
            from PyQt6.QtWidgets import QTableWidgetItem

            from frontend.app import PlannerWindow, create_app
            from frontend.formulacao import FormulaForm
            from frontend.pop import write_pop_docx

            app = create_app()
            window = PlannerWindow()
            assert len(window.catalog) == 10
            FormulaForm()  # Também lê o catálogo; precisa funcionar fora de locale UTF-8.
            window.protocol.setCurrentIndex(window.protocol.findData("PREP-001"))
            window.complete_protocol()
            window.percent_form.set_values(
                {
                    "base": "m/v",
                    "concentracao": 0.9,
                    "quantidade_final": 1000,
                    "pureza": 100,
                }
            )
            window.generate()
            assert abs(window.plan["resultado"]["quantidade_reagente"] - 9) < 1e-9
            window.navigate(4)
            assert window.percent_results.figure is None
            assert not window.percent_results.adjustments.isChecked()
            panel = window.analysis
            panel.unit.setText("mg/mL observado")
            panel.data.setItem(0, 0, QTableWidgetItem("Medições de teste"))
            for col, value in enumerate(("2", "4", "6"), 1):
                panel.data.setItem(0, col, QTableWidgetItem(value))
            panel.start_analysis()
            deadline = time.monotonic() + 60
            while panel.worker is not None and time.monotonic() < deadline:
                app.processEvents()
                time.sleep(0.01)
            assert panel.worker is None, "Análise não terminou em 60 segundos"
            assert panel.figure.axes
            assert panel.report["resumos"]["Medições de teste"]["media"] == 4
            from openpyxl import load_workbook

            from planejador.services.coleta import (
                conferir_coleta,
                exportar_modelo,
                organizar_coleta,
            )
            from planejador.services.exportacao_resultados import exportar_resultados
            from planejador.services.importacao_excel import read_workbook, recognize

            units = organizar_coleta(["Medições de teste"], 3, microplaca=True)
            collection = {"unidades": units, "unidade": panel.unit.text()}
            model = Path(directory) / "coleta.xlsx"
            exportar_modelo(
                model, units, {**panel.context, "coleta": collection}, panel.unit.text()
            )
            book = load_workbook(model)
            for row, value in enumerate((2, 4, 6), 2):
                book["Medições"].cell(row, 7, value)
            book.save(model)
            book.close()
            sheets = read_workbook(model)
            assert conferir_coleta(sheets, panel.context) == collection
            assert recognize(sheets["Medições"])[1] == {"Medições de teste": [2, 4, 6]}
            payload = panel.observation_payload()
            for extension in ("xlsx", "csv", "docx"):
                exportar_resultados(
                    Path(directory) / f"resultados.{extension}", payload
                )
            assert window.flush_observations()
            assert window.history.list()
            for protocol in window.catalog.values():
                path = Path(directory) / (protocol["id"] + ".docx")
                write_pop_docx(protocol, path)
                assert path.stat().st_size > 1000
            window.close()
            app.processEvents()
            window.history.engine.dispose()
            window.engine.dispose()
            report.update(
                ok=True,
                protocolos=10,
                massa_percentual_g=9,
                media_observada=4,
                pops_exportados=10,
                coleta_excel_conferida=True,
                exportacoes_resultados=3,
            )
    except Exception:
        report["ok"] = False
        report["erro"] = traceback.format_exc()
    Path(report_path).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0 if report["ok"] else 1
