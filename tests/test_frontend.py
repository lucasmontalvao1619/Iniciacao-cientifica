"""Verificações do fluxo sequencial e da busca integrada ao seletor."""

import json
import os

import pytest

pytest.importorskip("PyQt6", reason="Instale o extra ui para testar a interface.")
pytest.importorskip("matplotlib")

from PyQt6.QtCore import Qt  # noqa: E402
from PyQt6.QtTest import QTest  # noqa: E402

from frontend.app import PlannerWindow, create_app  # noqa: E402


@pytest.fixture(scope="module")
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return create_app()


def confirm(window, index=0):
    window.protocol.setCurrentIndex(index)
    window.complete_protocol()
    window.title.setText("Teste")


def test_wizard_reset_calculation_export(app, tmp_path):
    w = PlannerWindow()
    w.show()
    app.processEvents()
    assert w.protocol.currentIndex() == -1
    assert not w.steps[2].isEnabled()
    assert not w.steps[3].isEnabled()
    w.navigate(2)
    assert w.stack.currentIndex() == 0
    w.navigate(1)
    confirm(w)
    assert w.stack.currentIndex() == 2
    w.fields["n_amostras"].setValue(8)
    w.fields["n_replicatas"].setValue(3)
    w.fields["n_controles"].setValue(2)
    w.dilution.setChecked(True)
    w.generate()
    assert w.stack.currentIndex() == 3
    assert w.plan["n_reacoes"] == 26
    assert w.plan["preparo"]["diluicao"]["volume_alicota"] == 1
    path = tmp_path / "plan.json"
    w.write_export(path)
    assert json.loads(path.read_text())["demonstrativo"]
    w.navigate(2)
    w.fields["n_amostras"].setValue(3)
    assert w.plan is None
    assert not w.steps[3].isEnabled()
    assert w.table.rowCount() == 0
    w.navigate(3)
    assert w.stack.currentIndex() == 2
    w.generate()
    assert w.plan["n_reacoes"] == 11
    w.navigate(1)
    w.protocol.setCurrentIndex(1)
    assert not w.steps[2].isEnabled()
    assert w.title.text() == ""
    assert w.fields["n_amostras"].value() == 1
    assert not w.dilution.isChecked()
    w.complete_protocol()
    w.title.setText("Outro")
    w.generate()
    assert w.plan is not None
    w.new_planning()
    assert w.protocol.currentIndex() == -1
    assert w.plan is None
    assert w.title.text() == ""
    assert not w.steps[2].isEnabled()
    assert not w.steps[3].isEnabled()
    w.close()


def test_dropdown_search_keyboard_and_invalid_text(app):
    w = PlannerWindow()
    w.show()
    w.navigate(1)
    app.processEvents()
    assert w.protocol.isEditable()
    assert w.protocol.count() == 12
    c = w.protocol.completer()
    c.setCompletionPrefix("diluicao")
    assert c.completionCount() >= 3
    c.setCompletionPrefix("prep-004")
    assert c.completionCount() == 1
    assert "PREP-004" in c.currentCompletion()
    w.protocol.setEditText("inexistente")
    w.complete_protocol()
    assert not w.protocol_done
    assert w.stack.currentIndex() == 1
    confirm(w, 5)
    assert w.protocol_done
    w.generate()
    assert w.plan is None  # Catalog entry has no verified scientific implementation.
    assert not w.steps[3].isEnabled()
    w.navigate(1)
    w.protocol.lineEdit().setFocus()
    QTest.keyClicks(w.protocol.lineEdit(), "x")
    assert not w.protocol_done
    assert not w.steps[2].isEnabled()
    w.close()


def test_error_stays_in_parameters(app):
    w = PlannerWindow()
    confirm(w)
    w.dilution.setChecked(True)
    w.solution_fields["conc_final"].setValue(20)
    w.generate()
    assert w.stack.currentIndex() == 2
    assert w.error.text()
    assert not w.steps[3].isEnabled()
    w.close()


def test_integrated_results_and_reset(app, tmp_path):
    from PyQt6.QtWidgets import QTableWidgetItem

    from frontend.analysis import parse_measurements

    w = PlannerWindow()
    assert not w.steps[4].isEnabled()
    w.navigate(4)
    assert w.stack.currentIndex() == 0
    confirm(w)
    w.generate()
    w.navigate(4)
    assert w.stack.currentIndex() == 4
    panel = w.analysis
    assert panel.context["titulo"] == "Teste"
    assert panel.data.item(0, 1) is None
    panel.unit.setText("mg/mL")
    for i, (name, values) in enumerate(
        [("Controle", "1;2;3"), ("Tratamento", "3;4;5")]
    ):
        panel.data.setItem(i, 0, QTableWidgetItem(name))
        panel.data.setItem(i, 1, QTableWidgetItem(values))
    panel.analyze()
    assert panel.report["resumos"]["Controle"]["media"] == 2
    assert panel.report["resumos"]["Tratamento"]["media"] == 4
    assert panel.report["teste_t"] is None
    assert panel.report["experimento"]["protocolo"] == w.plan["protocolo"]
    assert panel.figure.axes[0].get_ylabel() == "mg/mL"
    assert panel.table.rowCount() == 2
    assert len(panel.figure.axes[0].collections) == 2
    panel.infer.setChecked(True)
    panel.analyze()
    assert panel.report["teste_t"] is not None
    bundle = tmp_path / "experimento.json"
    w.write_export(bundle)
    saved = json.loads(bundle.read_text())
    assert (
        saved["plano"]["protocolo"]
        == saved["resultados_observados"]["analise"]["experimento"]["protocolo"]
    )
    assert saved["resultados_observados"]["medicoes"]["Controle"] == [1, 2, 3]
    path = tmp_path / "plot.png"
    panel.figure.savefig(path)
    assert path.read_bytes().startswith(b"\x89PNG")
    panel.data.setItem(0, 1, QTableWidgetItem("nan"))
    assert panel.report is None
    assert not panel.save.isEnabled()
    panel.analyze()
    assert "finito" in panel.status.text()
    w.navigate(2)
    w.fields["n_amostras"].setValue(4)
    assert panel.context is None
    assert panel.data.item(0, 1) is None
    assert not w.steps[4].isEnabled()
    with pytest.raises(ValueError):
        parse_measurements("A;1;extra")
    assert parse_measurements("A;1,5") == {"A": [1.5]}
    w.close()


def test_click_field_opens_search_and_keeps_typing(app):
    w = PlannerWindow()
    w.show()
    w.navigate(1)
    app.processEvents()
    editor = w.protocol.lineEdit()
    QTest.mouseClick(editor, Qt.MouseButton.LeftButton)
    app.processEvents()
    popup = w.protocol.completer().popup()
    assert popup.isVisible()
    assert w.protocol.completer().completionCount() == 12
    QTest.keyClicks(editor, "prep-004")
    app.processEvents()
    assert w.protocol.completer().completionCount() == 1
    index = popup.model().index(0, 0)
    QTest.mouseClick(
        popup.viewport(),
        Qt.MouseButton.LeftButton,
        pos=popup.visualRect(index).center(),
    )
    app.processEvents()
    assert w.protocol.currentData() == "PREP-004"
    w.complete_protocol()
    assert w.protocol_done
    assert w.stack.currentIndex() == 2
    popup.hide()
    w.close()


def test_accessibility_sidebar_state_activates_page(app):
    w = PlannerWindow()
    w.steps[1].setChecked(True)
    assert w.stack.currentIndex() == 1
    assert not w.steps[0].isChecked()
    w.steps[0].setChecked(True)
    assert w.stack.currentIndex() == 0
    assert not w.steps[1].isChecked()
    w.close()
