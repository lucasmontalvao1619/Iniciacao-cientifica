"""Verificação do executável no CI, com dados descartáveis e sem janelas."""

import json
import os
import tempfile
import traceback
from pathlib import Path


def verify(report_path):
    report = {"ok": False}
    try:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
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
            panel = window.analysis
            panel.unit.setText("mg/mL observado")
            panel.data.setItem(0, 0, QTableWidgetItem("Medições de teste"))
            panel.data.setItem(0, 1, QTableWidgetItem("2;4;6"))
            panel.analyze()
            assert panel.report["resumos"]["Medições de teste"]["media"] == 4
            assert window.flush_observations()
            assert window.history.list()
            for protocol in window.catalog.values():
                path = Path(directory) / (protocol["id"] + ".docx")
                write_pop_docx(protocol, path)
                assert path.stat().st_size > 1000
            window.close()
            app.processEvents()
            report.update(
                ok=True,
                protocolos=10,
                massa_percentual_g=9,
                media_observada=4,
                pops_exportados=10,
            )
    except Exception:
        report["erro"] = traceback.format_exc()
    Path(report_path).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0 if report["ok"] else 1
