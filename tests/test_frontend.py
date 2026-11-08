"""Verificações do fluxo sequencial e da busca integrada ao seletor."""

import json
import os

import pytest

pytest.importorskip("PyQt6", reason="Instale o extra ui para testar a interface.")
pytest.importorskip("matplotlib")

from PyQt6.QtCore import Qt  # noqa: E402
from PyQt6.QtTest import QTest  # noqa: E402

from frontend.app import PlannerWindow, create_app  # noqa: E402


@pytest.fixture(autouse=True)
def isolate_history(monkeypatch, tmp_path):
    monkeypatch.setenv("PLANEJADOR_DATA_DIR", str(tmp_path / "dados"))
    yield
    # Falhas de largura precisam identificar a peça que impõe o mínimo no SO.
    from PyQt6.QtWidgets import QApplication, QScrollArea, QWidget

    for window in QApplication.topLevelWidgets():
        for area in window.findChildren(QScrollArea):
            if not area.isVisible() or area.horizontalScrollBar().maximum() == 0:
                continue
            print(
                "OVERFLOW",
                area.viewport().width(),
                area.widget().width(),
                QApplication.font().family(),
                QApplication.font().pointSize(),
                window.logicalDpiX(),
            )
            for widget in area.widget().findChildren(QWidget):
                if widget.isVisible() and widget.minimumSizeHint().width() > 350:
                    text = widget.text() if hasattr(widget, "text") else ""
                    print(type(widget).__name__, widget.minimumSizeHint().width(), text)


@pytest.fixture(scope="module")
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return create_app()


def confirm(window, index=None):
    if index is None:
        # Backend examples are test fixtures, absent from the app's catalog.
        from sqlalchemy.orm import Session

        from planejador.services import listar_protocolos

        if window.protocol.findData(1) < 0:
            with Session(window.engine) as session:
                demos = listar_protocolos(session)
            window.protocols.extend(demos)
            for position, item in enumerate(demos):
                window.protocol.insertItem(position, item["nome"], item["id"])
        index = window.protocol.findData(1)
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
    assert json.loads(path.read_text(encoding="utf-8"))["plano"]["n_reacoes"] == 26
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
    w.protocol.setCurrentIndex(w.protocol.findData(2))
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
    assert w.protocol.count() == 10
    assert all(w.protocol.itemText(i).startswith("PREP-") for i in range(10))
    assert all(str(item["id"]).startswith("PREP-") for item in w.protocols)
    c = w.protocol.completer()
    c.setCompletionPrefix("diluicao")
    assert c.completionCount() >= 2
    c.setCompletionPrefix("prep-004")
    assert c.completionCount() == 1
    assert "PREP-004" in c.currentCompletion()
    w.protocol.setEditText("inexistente")
    w.complete_protocol()
    assert not w.protocol_done
    assert w.stack.currentIndex() == 1
    confirm(w, w.protocol.findData("PREP-010"))
    assert w.protocol_done
    w.generate()
    assert w.plan is None
    assert "placas ou tubos" in w.error.text()
    assert not w.steps[3].isEnabled()
    assert not w.steps[4].isEnabled()
    w.navigate(4)
    assert w.stack.currentIndex() == 2
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
    saved = json.loads(bundle.read_text(encoding="utf-8"))
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
    assert w.protocol.completer().completionCount() == 10
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


def test_startup_defers_scientific_stack_until_results():
    import subprocess
    import sys
    from pathlib import Path

    code = """
import sys
from frontend.app import create_app, PlannerWindow
app = create_app()
w = PlannerWindow()
w.show()
app.processEvents()
assert w.analysis is None
assert not any(name in sys.modules for name in ('scipy', 'pandas', 'matplotlib', 'frontend.analysis'))
w.protocol.insertItem(0, "Exemplo de teste", 1)
w.protocol.setCurrentIndex(0)
w.complete_protocol()
w.title.setText('Carregamento')
w.generate()
assert w.analysis is None
assert 'scipy' not in sys.modules
w.navigate(4)
assert w.analysis is not None
assert w.analysis.context['titulo'] == 'Carregamento'
assert 'matplotlib' in sys.modules and 'scipy' in sys.modules
w.close()
"""
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        check=True,
        timeout=60,
    )


def test_unknown_calculation_type_does_not_fabricate_plan():
    from planejador.core.exceptions import EntradaInvalida
    from planejador.services.preparos import calcular_preparo

    with pytest.raises(EntradaInvalida, match="não estão implementadas"):
        calcular_preparo({"tipo_calculo": "nao_implementado"}, {})


def test_pop_in_protocol_page_is_specific_and_does_not_change_plan(app):
    from PyQt6.QtWidgets import QTextEdit

    w = PlannerWindow()
    w.show()
    w.navigate(1)
    assert not w.preview_button.isEnabled()
    assert not w.docx_button.isEnabled()
    texts = []
    for i in range(10):
        w.protocol.setCurrentIndex(i)
        protocol = w.selected_pop()
        assert protocol is not None
        assert w.stack.currentWidget().isAncestorOf(w.preview_button)
        w.preview_button.click()
        app.processEvents()
        dialog = app.activeModalWidget()
        text = dialog.findChild(QTextEdit).toPlainText()
        assert protocol["id"] in text and protocol["name"] in text
        assert (
            protocol["source_codes"] in text
            or protocol.get("fontes", [{}])[0].get("url", "__missing__") in text
        )
        assert "validação" in text or "não disponível" in text
        texts.append(text)
        assert w.stack.currentIndex() == 1
        assert not w.protocol_done
        assert w.plan is None
        dialog.accept()
    assert len(set(texts)) == 10
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    w.percent_form.soluto.setText("NaCl")
    w.percent_form.solvente.setText("Água")
    w.percent_form.concentracao.setValue(1)
    w.percent_form.quantidade_final.setValue(100)
    w.percent_form.pureza.setValue(100)
    w.plan_button.click()
    plan = w.plan
    assert plan is not None
    w.navigate(1)
    w.preview_button.click()
    app.processEvents()
    assert w.plan is plan
    app.activeModalWidget().accept()
    w.protocol.setEditText("não cadastrado")
    assert not w.preview_button.isEnabled()
    assert not w.docx_button.isEnabled()
    w.close()


def test_pop_docx_export_selected_protocol_cancel_and_error(app, tmp_path, monkeypatch):
    from docx import Document
    from PyQt6.QtWidgets import QFileDialog

    w = PlannerWindow()
    w.navigate(1)
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-010"))
    path = tmp_path / "POP.docx"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: (str(path), ""))
    w.docx_button.click()
    text = "\n".join(p.text for p in Document(path).paragraphs)
    assert (
        "PREP-010" in text
        and "Cálculo de meio necessário por número de placas/tubos" in text
    )
    assert "Anvisa" in text and "PDF 20" in text
    assert "Consulta PREP-010" in text
    assert "POP salvo" in w.pop_status.text()
    original = path.read_bytes()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("", ""))
    w.export_pop()
    assert path.read_bytes() == original
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(tmp_path / "missing" / "POP.docx"), ""),
    )
    w.export_pop()
    assert "Não foi possível salvar" in w.pop_status.text()
    assert w.stack.currentIndex() == 1
    w.close()


def test_clear_button_removes_protocol_selection_and_dependent_state(app):
    from PyQt6.QtWidgets import QToolButton

    w = PlannerWindow()
    w.show()
    confirm(w, w.protocol.findData("PREP-001"))
    w.percent_form.soluto.setText("NaCl")
    w.percent_form.solvente.setText("Água")
    w.percent_form.concentracao.setValue(1)
    w.percent_form.quantidade_final.setValue(100)
    w.percent_form.pureza.setValue(100)
    w.generate()
    w.navigate(1)
    app.processEvents()
    clear = w.protocol.lineEdit().findChild(QToolButton)
    assert clear is not None and clear.isVisible()
    QTest.mouseClick(clear, Qt.MouseButton.LeftButton)
    app.processEvents()
    assert w.protocol.currentText() == ""
    assert w.protocol.currentIndex() == -1
    assert w.protocol.currentData() is None
    assert "PREP-001" not in w.description.text()
    assert "Pesquise e selecione" in w.description.text()
    assert not w.protocol_done and w.plan is None
    assert not any(w.steps[i].isEnabled() for i in (2, 3, 4))
    assert not w.preview_button.isEnabled() and not w.docx_button.isEnabled()
    w.complete_protocol()
    assert w.stack.currentIndex() == 1
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-002"))
    w.complete_protocol()
    assert w.stack.currentIndex() == 2
    assert "PREP-002" in w.title.text()
    w.close()


def test_percentual_parameters_results_live_graph_and_export(app, tmp_path):
    from docx import Document

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    assert w.generic_parameters.isHidden()
    assert not w.percent_form.isHidden()
    w.percent_form.soluto.setText("Reagente indicado pelo pesquisador")
    w.percent_form.solvente.setText("Solvente indicado pelo pesquisador")
    w.percent_form.concentracao.setValue(0.9)
    w.percent_form.quantidade_final.setValue(1000)
    w.percent_form.pureza.setValue(100)
    w.generate()
    assert w.stack.currentIndex() == 3
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(
        9, rel=1e-12, abs=1e-12
    )
    w.navigate(4)
    panel = w.percent_results
    panel.form.quantidade_final.setValue(500)
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(
        4.5, rel=1e-12, abs=1e-12
    )
    assert panel.figure.axes[0].lines[0].get_ydata()[-1] == pytest.approx(
        4.5, rel=1e-12, abs=1e-12
    )
    assert w.percent_form.quantidade_final.value() == 500
    panel.form.soluto.clear()
    assert w.plan is not None
    panel.form.base.setCurrentIndex(panel.form.base.findData("v/v"))
    panel.form.pureza.setValue(0.1)
    assert w.plan is None and not panel.save.isEnabled()
    panel.form.pureza.setValue(100)
    panel.form.soluto.setText("Novo reagente")
    assert w.plan is not None and panel.save.isEnabled()
    path = tmp_path / "plano.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["fontes"][0]["year"] == 2009
    assert "resultados_observados" not in saved
    doc = tmp_path / "POP.docx"
    write_pop_docx(w.selected_pop(), doc)
    document = Document(doc)
    assert len(document.inline_shapes) == 1
    text = "\n".join(p.text for p in document.paragraphs)
    assert "US DEA" in text and "domínio público" in text.lower()
    assert "2009" in text and "prévia" not in text.lower()
    w.navigate(2)
    w.percent_form.quantidade_final.setValue(250)
    w.generate()
    w.navigate(4)
    assert w.percent_results.form.quantidade_final.value() == 250
    w.close()


def test_home_history_has_ten_and_archives_without_reopening(app):
    from PyQt6.QtWidgets import QTextEdit

    w = PlannerWindow()
    for i in range(11):
        w.history.save(
            {
                "titulo": f"Experimento {i}",
                "parametros": {"quantidade_final": 100},
                "plano": {
                    "protocolo": "PREP-001",
                    "reagentes": [],
                    "procedimento": ["Conferir procedimento"],
                },
            }
        )
    w.refresh_history()
    assert w.history_table.rowCount() == 10
    assert len(list(w.history.archive_dir.glob("*.json"))) == 1
    records = w.history.list()
    w.archive_record(records[0]["id"])
    assert w.history_table.rowCount() == 9
    payload = json.loads(
        list(w.history.archive_dir.glob("*.json"))[0].read_text(encoding="utf-8")
    )
    w.view_record(payload)
    app.processEvents()
    dialog = app.activeModalWidget()
    assert dialog.findChild(QTextEdit).isReadOnly()
    assert "Experimento" in dialog.findChild(QTextEdit).toPlainText()
    assert w.plan is None and w.stack.currentIndex() == 0
    dialog.accept()
    w.close()


def test_molar_custom_form_live_results_history_and_protocol_switch(app, tmp_path):
    from docx import Document

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-002"))
    w.complete_protocol()
    form = w.percent_form
    assert form.tipo == "molar" and form.base.isHidden()
    assert not form.massa_molar.isHidden() and form.densidade.isHidden()
    form.soluto.setText("Forma química escolhida pelo pesquisador")
    form.solvente.setText("Solvente do experimento")
    form.concentracao.setValue(0.1)
    form.quantidade_final.setValue(1000)
    form.pureza.setValue(100)
    w.generate()
    assert w.plan is None and "Massa molar" in w.error.text()
    form.massa_molar.setValue(58.44)
    form.concentracao.setValue(0.1)
    form.quantidade_final.setValue(1000)
    w.generate()
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(5.844)
    record_id = w.history_id
    w.navigate(4)
    panel = w.percent_results
    panel.form.quantidade_final.setValue(500)
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(2.922)
    assert panel.figure.axes[0].lines[0].get_ydata()[-1] == pytest.approx(2.922)
    assert "mol/L" in panel.figure.axes[0].get_title()
    assert w.history_id == record_id and len(w.history.list()) == 1
    panel.form.forma.setCurrentIndex(panel.form.forma.findData("volume"))
    assert not panel.form.densidade.isHidden()
    assert w.plan is None and not panel.save.isEnabled()
    panel.form.densidade.setValue(1.2)
    assert w.plan["resultado"]["unidade_reagente"] == "mL"
    assert "base" not in w.parameters
    assert w.percent_form.forma.currentData() == "volume"
    path = tmp_path / "molar.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["protocolo_id"] == "PREP-002"
    assert saved["plano"]["fontes"][0]["paginas"][-2:] == [249, 250]
    doc = tmp_path / "molar.docx"
    write_pop_docx(w.selected_pop(), doc)
    document = Document(doc)
    text = "\n".join(p.text for p in document.paragraphs)
    assert len(document.inline_shapes) == 1
    assert "Hannes Grobe" in text and "CC BY-SA 2.5" in text
    assert "Densidade" in text or "densidade" in text
    w.new_planning()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    assert form.tipo == "percentual"
    assert not form.base.isHidden() and form.massa_molar.isHidden()
    assert form.soluto.text() == "" and w.plan is None
    w.close()


def test_variable_questions_start_without_assuming_physical_values(app):
    w = PlannerWindow()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    form = w.percent_form
    for field in (form.concentracao, form.quantidade_final, form.pureza):
        assert field.value() == 0
        assert form.form.labelForField(field).text().endswith("?")
    w.generate()
    assert w.plan is None
    form.concentracao.setValue(1)
    form.quantidade_final.setValue(100)
    form.pureza.setValue(100)
    w.generate()
    assert (
        w.plan is not None
    )  # Substance identity is optional for the numeric calculation.
    assert w.parameters["soluto"] == "" and w.parameters["solvente"] == ""
    assert w.plan["reagentes"][0]["nome"] == "Reagente não identificado"
    w.close()


def test_stock_questions_equivalence_live_graph_optional_label_and_export(
    app, tmp_path
):
    from docx import Document

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-003"))
    w.complete_protocol()
    form = w.percent_form
    assert form.tipo == "estoque" and not form.unidade_estoque.isHidden()
    assert form.base.isHidden() and form.metadata_widget.isHidden()
    form.unidade_estoque.setCurrentIndex(form.unidade_estoque.findData("µg/mL"))
    form.correcao.setCurrentIndex(form.correcao.findData("atividade"))
    form.concentracao.setValue(10000)
    form.quantidade_final.setValue(1)
    form.potencia.setValue(7760)
    w.generate()
    assert w.plan is None and "equivalência" in w.error.text()
    assert not form.equivalencia.isHidden()
    form.equivalencia.setValue(10)
    w.generate()
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(10000 / 776)
    assert w.plan["pendencias_rotulo"]
    record = w.history_id
    w.navigate(4)
    panel = w.percent_results
    panel.form.equivalencia.setValue(20)
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(20000 / 776)
    assert panel.figure.axes[0].lines[0].get_ydata()[-1] == pytest.approx(20000 / 776)
    assert w.history_id == record
    panel.form.unidade_estoque.setCurrentIndex(
        panel.form.unidade_estoque.findData("U/mL")
    )
    assert panel.form.equivalencia.isHidden()
    assert "equivalencia" not in w.parameters
    assert "U/mL" in panel.figure.axes[0].get_title()
    panel.form.metadata_group.setChecked(True)
    panel.form.meta_fields["data_validade"].setText("Data incompleta")
    assert w.plan is not None and "data_validade" in w.plan["erros_rotulo"]
    assert panel.save.isEnabled()
    path = tmp_path / "estoque.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["plano"]["rotulo_planejado"]["data_validade"] == "Data incompleta"
    assert len(saved["fontes"]) == 2
    doc = tmp_path / "POP-003.docx"
    write_pop_docx(w.selected_pop(), doc)
    document = Document(doc)
    text = "\n".join(p.text for p in document.paragraphs)
    assert "Anvisa" in text and "US DEA" in text and "equivalência" in text
    assert len(document.inline_shapes) == 1
    w.new_planning()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-002"))
    w.complete_protocol()
    assert form.unidade_estoque.isHidden() and form.equivalencia.isHidden()
    assert form.massa_molar.value() == 0
    w.close()


def test_stock_questions_fit_minimum_window_width(app):
    from PyQt6.QtWidgets import QScrollArea

    w = PlannerWindow()
    w.show()
    w.resize(880, 640)
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-003"))
    w.complete_protocol()
    form = w.percent_form
    form.metadata_group.setChecked(True)
    for unit in ("mg/mL", "mol/L", "U/mL"):
        form.unidade_estoque.setCurrentIndex(form.unidade_estoque.findData(unit))
        form.forma.setCurrentIndex(form.forma.findData("volume"))
        app.processEvents()
        visible = [area for area in w.findChildren(QScrollArea) if area.isVisible()]
        assert visible and all(
            area.horizontalScrollBar().maximum() == 0 for area in visible
        )
        assert form.note.height() >= form.note.heightForWidth(form.note.width())
    w.close()


def test_stock_dilution_questions_plan_graph_export_and_switch(app, tmp_path):
    from docx import Document
    from PyQt6.QtWidgets import QScrollArea

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.resize(880, 640)
    w.show()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-004"))
    w.complete_protocol()
    form = w.percent_form
    assert form.tipo == "diluicao"
    assert form.pureza.isHidden() and form.massa_molar.isHidden()
    assert form.metadata_group.isHidden() and form.forma.isHidden()
    assert form.concentracao_inicial.value() == 0
    form.unidade_diluicao.setCurrentIndex(form.unidade_diluicao.findData("mol/L"))
    form.concentracao_inicial.setValue(1)
    form.concentracao.setValue(0.1)
    form.quantidade_final.setValue(10)
    app.processEvents()
    assert all(
        s.horizontalScrollBar().maximum() == 0
        for s in w.findChildren(QScrollArea)
        if s.isVisible()
    )
    w.generate()
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(1)
    assert (
        "Alíquota" in w.summary.text() and "Fator de diluição: 10" in w.summary.text()
    )
    assert "pureza" not in w.parameters and "base" not in w.parameters
    record = w.history_id
    w.navigate(4)
    panel = w.percent_results
    panel.form.concentracao_inicial.setValue(2)
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(0.5)
    assert panel.figure.axes[0].lines[0].get_ydata()[-1] == pytest.approx(0.5)
    assert "mol/L" in panel.figure.axes[0].get_title()
    assert "Alíquota" in panel.figure.axes[0].get_ylabel()
    assert w.history_id == record
    path = tmp_path / "diluicao.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["plano"]["concentracao_estoque"]["valor"] == 2
    assert saved["plano"]["resultado"]["volume_diluente_nominal"] == pytest.approx(9.5)
    assert saved["fontes"][0]["paginas"] == [230, 231, 232]
    panel.form.concentracao.setValue(3)
    assert w.plan is None and not panel.save.isEnabled()
    assert not panel.figure.axes
    panel.form.concentracao.setValue(2)
    assert w.plan["resultado"]["fator_diluicao"] == 1
    assert "sem necessidade" in panel.summary.text()
    doc = tmp_path / "POP-004.docx"
    write_pop_docx(w.selected_pop(), doc)
    document = Document(doc)
    text = "\n".join(p.text for p in document.paragraphs)
    assert "C1 × V1" in text and "Hannes Grobe" in text and "q.s.p." in text
    assert len(document.inline_shapes) == 1
    w.new_planning()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    assert (
        form.concentracao_inicial.isHidden() and form.concentracao_inicial.value() == 0
    )
    assert not form.pureza.isHidden()
    w.close()


def test_serial_questions_tables_live_graph_and_export(app, tmp_path):
    from docx import Document
    from PyQt6.QtWidgets import QScrollArea

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.show()
    w.resize(880, 640)
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-005"))
    w.complete_protocol()
    f = w.percent_form
    assert f.tipo == "seriada" and f.concentracao.isHidden() and f.pureza.isHidden()
    assert f.n_diluicoes.value() == 0 and f.fator.value() == 0
    f.concentracao_inicial.setValue(100)
    f.fator.setValue(10)
    f.n_diluicoes.setValue(3)
    f.quantidade_final.setValue(10)
    app.processEvents()
    assert all(
        s.horizontalScrollBar().maximum() == 0
        for s in w.findChildren(QScrollArea)
        if s.isVisible()
    )
    w.generate()
    assert w.serie_table.rowCount() == 3
    assert "concentracao" not in w.parameters and "pureza" not in w.parameters
    assert w.plan["etapas"][-1]["concentracao"] == pytest.approx(0.1)
    record = w.history_id
    w.navigate(4)
    panel = w.percent_results
    assert panel.serie_table.rowCount() == 3
    assert panel.figure.axes[0].get_yscale() == "log"
    assert list(panel.figure.axes[0].lines[0].get_ydata()) == pytest.approx(
        [100, 10, 1, 0.1]
    )
    panel.form.igualar_ultimo.setChecked(True)
    assert w.plan["etapas"][-1]["volume_restante_mL"] == pytest.approx(9)
    panel.form.fator.setValue(2)
    assert panel.figure.axes[0].lines[0].get_ydata()[-1] == pytest.approx(12.5)
    assert w.history_id == record
    path = tmp_path / "serie.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert len(saved["plano"]["etapas"]) == 3 and len(saved["fontes"]) == 2
    assert saved["plano"]["igualar_ultimo"]
    panel.form.fator.setValue(1)
    assert (
        w.plan is None and panel.serie_table.rowCount() == 0 and not panel.figure.axes
    )
    panel.form.fator.setValue(10)
    panel.form.concentracao_inicial.setValue(0.000001)
    panel.form.n_diluicoes.setValue(51)
    panel.form.fator.setValue(1000000)
    assert w.plan is not None and panel.serie_table.rowCount() == 51
    panel.canvas.draw()
    assert panel.figure.axes[0].get_ylim()[0] > 0
    doc = tmp_path / "POP005.docx"
    write_pop_docx(w.selected_pop(), doc)
    d = Document(doc)
    text = "\n".join(p.text for p in d.paragraphs)
    assert len(d.inline_shapes) == 1 and "Hannes Grobe" in text and "441–442" in text
    assert "não confirmado" in text
    w.new_planning()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-004"))
    w.complete_protocol()
    assert (
        f.fator.isHidden()
        and f.n_diluicoes.isHidden()
        and not f.concentracao.isHidden()
    )
    assert not f.igualar_ultimo.isChecked()
    w.close()


def test_factor_questions_graph_live_export_and_switch(app, tmp_path):
    from docx import Document
    from PyQt6.QtWidgets import QScrollArea

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.show()
    w.resize(880, 640)
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-006"))
    w.complete_protocol()
    f = w.percent_form
    assert f.tipo == "fator" and f.concentracao.isHidden() and f.pureza.isHidden()
    assert f.volume_alicota.value() == 0 and not f.volume_alicota.isHidden()
    f.concentracao_inicial.setValue(100)
    f.volume_alicota.setValue(1)
    f.quantidade_final.setValue(10)
    app.processEvents()
    assert all(
        s.horizontalScrollBar().maximum() == 0
        for s in w.findChildren(QScrollArea)
        if s.isVisible()
    )
    w.generate()
    assert w.plan["resultado"]["concentracao_calculada"] == pytest.approx(10)
    assert w.serie_table.isHidden()
    assert "concentracao" not in w.parameters and "pureza" not in w.parameters
    assert "Concentração final calculada" in w.summary.text()
    record = w.history_id
    w.navigate(4)
    panel = w.percent_results
    panel.form.quantidade_final.setValue(20)
    assert w.plan["resultado"]["concentracao_calculada"] == pytest.approx(5)
    assert w.plan["resultado"]["fator_diluicao"] == pytest.approx(20)
    panel.form.volume_alicota.setValue(2)
    assert w.plan["resultado"]["concentracao_calculada"] == pytest.approx(10)
    ax = panel.figure.axes[0]
    assert ax.lines[0].get_ydata()[-1] == pytest.approx(10)
    assert ax.collections[0].get_offsets()[0].tolist() == pytest.approx([20, 10])
    assert w.history_id == record
    path = tmp_path / "fator.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["plano"]["resultado"]["concentracao_calculada"] == 10
    assert saved["parametros"]["volume_alicota"] == 2
    panel.form.volume_alicota.setValue(21)
    assert w.plan is None and not panel.figure.axes and not panel.save.isEnabled()
    panel.form.volume_alicota.setValue(20)
    assert w.plan["resultado"]["fator_diluicao"] == 1
    doc = tmp_path / "POP006.docx"
    write_pop_docx(w.selected_pop(), doc)
    d = Document(doc)
    text = "\n".join(p.text for p in d.paragraphs)
    assert len(d.inline_shapes) == 1 and "F = V2/V1" in text and "Hannes Grobe" in text
    w.new_planning()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-005"))
    w.complete_protocol()
    assert f.volume_alicota.isHidden() and f.volume_alicota.value() == 0
    assert not f.n_diluicoes.isHidden()
    w.close()


def test_volume_questions_live_totals_units_graph_and_export(app, tmp_path):
    from docx import Document
    from PyQt6.QtWidgets import QScrollArea

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.show()
    w.resize(880, 640)
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-007"))
    w.complete_protocol()
    f = w.percent_form
    assert (
        f.tipo == "volume"
        and f.base.isHidden()
        and f.pureza.isHidden()
        and f.solvente.isHidden()
    )
    assert f.concentracao_inicial.isHidden() and f.concentracao.isHidden()
    assert f.n_unidades.value() == 0 and f.quantidade_final.value() == 0
    assert f.excesso_volume.value() == 0 and f.unidade_volume.currentData() == "µL"
    f.quantidade_final.setValue(20)
    f.n_unidades.setValue(10)
    f.excesso_volume.setValue(10)
    app.processEvents()
    assert all(
        s.horizontalScrollBar().maximum() == 0
        for s in w.findChildren(QScrollArea)
        if s.isVisible()
    )
    w.generate()
    assert w.plan["resultado"]["quantidade_final"] == pytest.approx(220)
    assert "concentracao" not in w.parameters and "pureza" not in w.parameters
    assert "Volume base: 200" in w.summary.text() and "Fontes:" in w.summary.text()
    record = w.history_id
    w.navigate(4)
    panel = w.percent_results
    panel.form.n_unidades.setValue(20)
    assert w.plan["resultado"]["quantidade_final"] == pytest.approx(440)
    assert panel.figure.axes[0].lines[1].get_ydata()[-1] == pytest.approx(440)
    assert w.history_id == record
    panel.form.unidade_volume.setCurrentIndex(panel.form.unidade_volume.findData("mL"))
    assert (
        w.parameters["unidade_volume"] == "mL"
        and "mL" in panel.figure.axes[0].get_ylabel()
    )
    assert panel.form.quantidade_final.value() == 20
    panel.form.excesso_volume.setValue(0)
    assert w.plan["resultado"]["volume_excedente"] == 0
    assert len(panel.figure.axes[0].lines) == 1
    path = tmp_path / "volume.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["parametros"]["unidade_volume"] == "mL"
    assert saved["fontes"][0]["paginas_pdf"] == [49]
    panel.form.n_unidades.setValue(0)
    assert w.plan is None and not panel.figure.axes and not panel.save.isEnabled()
    panel.form.n_unidades.setValue(1000000)
    assert len(panel.figure.axes[0].lines[0].get_xdata()) <= 21
    doc = tmp_path / "POP007.docx"
    write_pop_docx(w.selected_pop(), doc)
    d = Document(doc)
    text = "\n".join(p.text for p in d.paragraphs)
    assert (
        len(d.inline_shapes) == 1
        and "Emicropipette" in text
        and "978-85-334-2402-9" in text
    )
    w.new_planning()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-006"))
    w.complete_protocol()
    assert (
        f.n_unidades.isHidden()
        and f.excesso_volume.isHidden()
        and f.unidade_volume.isHidden()
    )
    assert not f.volume_alicota.isHidden() and not f.solvente.isHidden()
    w.close()


def test_formula_reference_custom_questions_live_results_and_export(app, tmp_path):
    from docx import Document
    from PyQt6.QtWidgets import QScrollArea, QTableWidgetItem

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.show()
    w.resize(880, 640)
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-008"))
    w.complete_protocol()
    f = w.percent_form.formula_form
    assert f.table.rowCount() == 4 and f.source.isReadOnly()
    assert f.target.value() == 0 and not f.add.isEnabled()
    assert f.storage.isReadOnly() and "4 a 8" in f.storage.text()
    f.target.setValue(250)
    app.processEvents()
    assert all(
        s.horizontalScrollBar().maximum() == 0
        for s in w.findChildren(QScrollArea)
        if s.isVisible()
    )
    w.generate()
    assert w.plan["reagentes"][0]["quantidade_total"] == pytest.approx(0.75)
    assert "concentracao" not in w.parameters
    record = w.history_id
    w.navigate(4)
    panel = w.percent_results
    out = panel.form.formula_form
    assert panel.serie_table.rowCount() == 4
    out.target.setValue(500)
    assert w.plan["reagentes"][0]["quantidade_total"] == pytest.approx(1.5)
    assert panel.figure.axes[0].lines[0].get_ydata()[-1] == pytest.approx(1.5)
    panel.component_plot.setCurrentIndex(3)
    assert "mL" in panel.figure.axes[0].get_ylabel()
    assert panel.figure.axes[0].lines[0].get_ydata()[-1] == pytest.approx(500)
    assert w.history_id == record
    out.cycle.setText("Ciclo do laboratório")
    out.mode.setCurrentIndex(out.mode.findData("pesquisador"))
    assert out.cycle.text() == "" and not out.source.isReadOnly()
    assert w.plan is None
    out.base.setValue(100)
    out.source.setText("Receita própria, v1")
    out.table.setItem(0, 0, QTableWidgetItem("Componente A"))
    out.table.cellWidget(0, 1).setValue(2)
    out.add.click()
    assert w.plan is None
    out.table.setItem(1, 0, QTableWidgetItem("Água"))
    out.table.cellWidget(1, 1).setValue(100)
    out.table.cellWidget(1, 2).setCurrentText("mL")
    assert w.plan is not None and "pesquisador" in w.plan["formula_origem"]
    assert [x["quantidade_total"] for x in w.plan["reagentes"]] == pytest.approx(
        [10, 500]
    )
    path = tmp_path / "formula.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert (
        saved["parametros"]["fonte_formula"] == "Receita própria, v1"
        and saved["plano"]["pendencias_preparo"]
    )
    doc = tmp_path / "POP008.docx"
    write_pop_docx(w.selected_pop(), doc)
    d = Document(doc)
    text = "\n".join(p.text for p in d.paragraphs)
    assert (
        len(d.inline_shapes) == 1
        and "extrato de carne" in text.lower()
        and "US DEA" in text
        and "PDF 17" in text
    )
    w.new_planning()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    assert (
        w.percent_form.formula_form.isHidden()
        and not w.percent_form.concentracao.isHidden()
    )
    assert not w.percent_form.pureza.isHidden()
    w.close()


def test_commercial_medium_questions_live_graph_provenance_export_and_switch(
    app, tmp_path
):
    from docx import Document
    from PyQt6.QtWidgets import QScrollArea

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.show()
    w.resize(880, 640)
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-009"))
    w.complete_protocol()
    f = w.percent_form.comercial_form
    assert f.volume_type.currentData() is None
    assert all(field.value() == 0 for field in f.fields.values())
    f.fields["massa_referencia_g"].setValue(26)
    f.fields["volume_referencia_mL"].setValue(1000)
    f.fields["volume_alvo_mL"].setValue(250)
    f.texts["referencia_fabricante"].setText("Instrução declarada para teste, v1")
    w.generate()
    assert w.plan is None and "volume" in w.error.text()
    f.volume_type.setCurrentIndex(f.volume_type.findData("agua"))
    app.processEvents()
    assert all(
        s.horizontalScrollBar().maximum() == 0
        for s in w.findChildren(QScrollArea)
        if s.isVisible()
    )
    assert f.note.height() >= f.note.heightForWidth(f.note.width())
    w.generate()
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(6.5)
    assert "Instrução declarada" in w.summary.text()
    record = w.history_id
    w.navigate(4)
    panel = w.percent_results
    out = panel.form.comercial_form
    out.fields["volume_alvo_mL"].setValue(500)
    assert w.plan["resultado"]["quantidade_reagente"] == pytest.approx(13)
    assert panel.figure.axes[0].lines[0].get_ydata()[-1] == pytest.approx(13)
    assert "água" in panel.figure.axes[0].get_xlabel()
    out.volume_type.setCurrentIndex(out.volume_type.findData("final"))
    assert (
        "q.s.p." in w.plan["solvente"] and "final" in panel.figure.axes[0].get_xlabel()
    )
    assert w.history_id == record
    path = tmp_path / "meio.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert (
        saved["plano"]["fonte_fabricante_declarada"]["referencia"]
        == "Instrução declarada para teste, v1"
    )
    assert saved["parametros"]["tipo_volume"] == "final"
    out.fields["massa_referencia_g"].setValue(0)
    assert w.plan is None and not panel.save.isEnabled() and not panel.figure.axes
    out.fields["massa_referencia_g"].setValue(26)
    doc = tmp_path / "POP009.docx"
    write_pop_docx(w.selected_pop(), doc)
    d = Document(doc)
    text = "\n".join(p.text for p in d.paragraphs)
    assert (
        len(d.inline_shapes) == 1
        and "fabricante" in text
        and "US DEA" in text
        and "PREP-009" in text
    )
    w.new_planning()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-008"))
    w.complete_protocol()
    assert (
        w.percent_form.comercial_form.isHidden()
        and not w.percent_form.formula_form.isHidden()
    )
    w.new_planning()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    assert (
        w.percent_form.formula_form.isHidden()
        and w.percent_form.comercial_form.isHidden()
    )
    assert not w.percent_form.pureza.isHidden()
    w.close()


def test_recipients_questions_live_graph_history_export_and_reset(app, tmp_path):
    from docx import Document
    from PyQt6.QtWidgets import QScrollArea

    from frontend.pop import write_pop_docx

    w = PlannerWindow()
    w.show()
    w.resize(880, 640)
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-010"))
    w.complete_protocol()
    f = w.percent_form
    assert f.recipiente.currentData() is None
    assert f.unidade_volume.currentData() == "mL"
    assert f.n_unidades.value() == f.quantidade_final.value() == 0
    assert not f.recipiente.isHidden() and f.pureza.isHidden()
    w.generate()
    assert w.plan is None and "placas ou tubos" in w.error.text()
    f.set_values(
        {
            "recipiente": "placas",
            "unidade_volume": "mL",
            "volume_unitario": 20,
            "n_unidades": 12,
            "excesso_percentual": 10,
            "soluto": "Meio teste",
            "formato_recipiente": "90 mm",
            "metodo_distribuicao": "Método declarado v1",
        }
    )
    app.processEvents()
    assert all(
        s.horizontalScrollBar().maximum() == 0
        for s in w.findChildren(QScrollArea)
        if s.isVisible()
    )
    assert f.note.height() >= f.note.heightForWidth(f.note.width())
    w.generate()
    assert w.plan["resultado"]["quantidade_final"] == 264
    assert "12 placas" in w.summary.text()
    record = w.history_id
    w.navigate(4)
    panel = w.percent_results
    out = panel.form
    out.n_unidades.setValue(20)
    assert w.plan["resultado"]["quantidade_final"] == pytest.approx(440)
    assert panel.figure.axes[0].lines[-1].get_ydata()[-1] == pytest.approx(440)
    assert panel.figure.axes[0].get_xlabel() == "Número de placas"
    out.recipiente.setCurrentIndex(out.recipiente.findData("tubos"))
    out.quantidade_final.setValue(6)
    assert w.plan["resultado"]["quantidade_final"] == pytest.approx(132)
    assert panel.figure.axes[0].get_xlabel() == "Número de tubos"
    assert w.history_id == record
    path = tmp_path / "recipientes.json"
    w.write_export(path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["parametros"]["recipiente"] == "tubos"
    assert (
        saved["plano"]["distribuicao"]["metodo_distribuicao"] == "Método declarado v1"
    )
    assert len(saved["fontes"]) == 2
    out.n_unidades.setValue(0)
    assert w.plan is None and not panel.save.isEnabled() and not panel.figure.axes
    out.n_unidades.setValue(20)
    doc = tmp_path / "POP010.docx"
    write_pop_docx(w.selected_pop(), doc)
    d = Document(doc)
    text = "\n".join(p.text for p in d.paragraphs)
    assert len(d.inline_shapes) == 1 and "Hannes Grobe" in text and "PDF 20" in text
    assert "Não calcula massa de pó" in text
    w.new_planning()
    assert w.plan is None and f.recipiente.currentData() is None
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    assert f.recipiente.isHidden() and f.formato_recipiente.isHidden()
    assert not f.pureza.isHidden()
    w.close()


@pytest.mark.parametrize(
    "number,params",
    [
        (
            1,
            {
                "base": "m/v",
                "concentracao": 0.9,
                "quantidade_final": 1000,
                "pureza": 100,
            },
        ),
        (
            2,
            {
                "concentracao": 0.1,
                "quantidade_final": 1000,
                "massa_molar": 58.44,
                "pureza": 100,
                "forma": "pesagem",
            },
        ),
        (
            3,
            {
                "unidade_concentracao": "mg/mL",
                "concentracao": 1,
                "quantidade_final": 100,
                "pureza": 100,
                "correcao": "pureza",
                "forma": "pesagem",
            },
        ),
        (
            4,
            {
                "unidade_concentracao": "mg/mL",
                "concentracao_inicial": 10,
                "concentracao": 1,
                "quantidade_final": 100,
            },
        ),
        (
            5,
            {
                "unidade_concentracao": "mg/mL",
                "concentracao_inicial": 10,
                "fator": 2,
                "n_diluicoes": 3,
                "quantidade_final": 10,
            },
        ),
        (
            6,
            {
                "unidade_concentracao": "mg/mL",
                "concentracao_inicial": 10,
                "volume_alicota": 1,
                "quantidade_final": 10,
            },
        ),
        (
            7,
            {
                "unidade_volume": "mL",
                "volume_unitario": 5,
                "n_unidades": 10,
                "excesso_percentual": 10,
            },
        ),
        (8, {"formulacao_id": "anvisa_agar_nutriente", "volume_alvo_mL": 250}),
        (
            9,
            {
                "massa_referencia_g": 26,
                "volume_referencia_mL": 1000,
                "volume_alvo_mL": 250,
                "tipo_volume": "agua",
                "referencia_fabricante": "Rótulo declarado v1",
            },
        ),
        (
            10,
            {
                "recipiente": "placas",
                "unidade_volume": "mL",
                "volume_unitario": 20,
                "n_unidades": 12,
                "excesso_percentual": 10,
            },
        ),
    ],
)
def test_observations_associate_with_each_real_protocol_and_clear_on_plan_edit(
    app, tmp_path, number, params
):
    from PyQt6.QtWidgets import QTableWidgetItem

    w = PlannerWindow()
    code = f"PREP-{number:03}"
    w.protocol.setCurrentIndex(w.protocol.findData(code))
    w.complete_protocol()
    w.percent_form.set_values(params)
    w.generate()
    assert w.plan is not None, w.error.text()
    record = w.history_id
    w.navigate(4)
    panel = w.analysis
    assert panel.context["protocolo_id"] == code
    assert panel.data.item(0, 1) is None
    assert not w.observations_group.isChecked()
    w.observations_group.setChecked(True)
    panel.unit.setText("mg/mL observado")
    panel.data.setItem(0, 0, QTableWidgetItem("Lote A"))
    panel.data.setItem(0, 1, QTableWidgetItem("2;4;6"))
    panel.analyze()
    if number == 1:
        from PyQt6.QtWidgets import QScrollArea

        w.resize(880, 640)
        w.show()
        app.processEvents()
        assert all(
            scroll.horizontalScrollBar().maximum() == 0
            for scroll in w.findChildren(QScrollArea)
            if scroll.isVisible()
        )
    assert panel.report["resumos"]["Lote A"]["media"] == 4
    assert panel.report["resumos"]["Lote A"]["variancia"] == 4
    assert panel.report["resumos"]["Lote A"]["desvio_padrao"] == 2
    assert panel.report["teste_t"] is None
    assert panel.figure.axes[0].collections[0].get_offsets()[:, 1].tolist() == [2, 4, 6]
    target = tmp_path / f"{code}.json"
    w.write_export(target)
    saved = json.loads(target.read_text(encoding="utf-8"))
    assert saved["resultados_observados"]["estado"] == "analisado"
    assert (
        saved["resultados_observados"]["analise"]["experimento"]["protocolo_id"]
        == saved["protocolo_id"]
        == code
    )
    if number == 1:
        QTest.qWait(500)
        assert not w.observation_timer.isActive()
    else:
        w.flush_observations()
    stored = json.loads(w.history.list()[0]["conteudo"])
    assert stored["resultados_observados"]["medicoes"]["Lote A"] == [2, 4, 6]
    assert len(w.history.list()) == 1 and w.history_id == record
    w.navigate(3)
    w.navigate(4)
    assert w.analysis is panel and panel.report is not None
    updated = w.percent_results.form.values()
    quantity = (
        "volume_alvo_mL"
        if number in {8, 9}
        else "volume_unitario"
        if number in {7, 10}
        else "quantidade_final"
    )
    updated[quantity] += 1
    w.percent_results.form.set_values(updated)
    assert w.plan is not None
    assert panel.data.item(0, 1) is None and panel.report is None
    assert panel.context["protocolo_id"] == code
    assert "resultados_observados" not in w.export_payload()
    assert "resultados_observados" not in json.loads(w.history.list()[0]["conteudo"])
    if number == 10:
        panel.data.setItem(0, 0, QTableWidgetItem("Rascunho antes de arquivar"))
        panel.data.setItem(0, 1, QTableWidgetItem("3;pendente"))
        assert w.observation_timer.isActive()
        w.archive_record(record)
        archived = json.loads(
            next(w.history.archive_dir.glob("*.json")).read_text(encoding="utf-8")
        )
        assert (
            archived["experimento"]["resultados_observados"]["linhas_informadas"][0][
                "valores"
            ]
            == "3;pendente"
        )
        QTest.qWait(500)
        assert not w.history.list()
    w.close()


def test_observation_drafts_survive_close_archive_and_readonly_consultation(
    app, tmp_path
):
    from PyQt6.QtWidgets import QTableWidgetItem, QTextEdit

    w = PlannerWindow()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    w.percent_form.set_values(
        {"base": "m/v", "concentracao": 1, "quantidade_final": 100, "pureza": 100}
    )
    w.generate()
    record = w.history_id
    w.navigate(4)
    panel = w.analysis
    panel.unit.setText("Grandeza escolhida")
    panel.data.setItem(0, 0, QTableWidgetItem("Lote incompleto"))
    panel.data.setItem(0, 1, QTableWidgetItem("1;valor pendente"))
    assert panel.report is None
    w.close()  # No delay: the pending draft must be flushed before closing.
    reopened = PlannerWindow()
    stored = json.loads(reopened.history.list()[0]["conteudo"])
    observed = stored["resultados_observados"]
    assert observed["estado"] == "rascunho" and "analise" not in observed
    assert observed["linhas_informadas"][0]["valores"] == "1;valor pendente"
    reopened.history_id = record
    reopened.archive_record(record)
    assert not reopened.history.list()
    archived = json.loads(
        next(reopened.history.archive_dir.glob("*.json")).read_text(encoding="utf-8")
    )
    assert archived["experimento"]["resultados_observados"] == observed
    reopened.view_record(archived)
    app.processEvents()
    text = app.activeModalWidget().findChild(QTextEdit)
    assert text.isReadOnly() and "Lote incompleto" in text.toPlainText()
    assert "rascunho" in text.toPlainText()
    app.activeModalWidget().accept()
    reopened.close()


def test_undefined_statistic_does_not_leave_exportable_nan_analysis(app):
    from PyQt6.QtWidgets import QTableWidgetItem

    w = PlannerWindow()
    confirm(w)
    w.generate()
    w.navigate(4)
    panel = w.analysis
    panel.unit.setText("unidade")
    for row, name in enumerate(["A", "B"]):
        panel.data.setItem(row, 0, QTableWidgetItem(name))
        panel.data.setItem(row, 1, QTableWidgetItem("1;1;1"))
    panel.infer.setChecked(True)
    panel.analyze()
    assert panel.report is None and not panel.save.isEnabled()
    assert "indefinido" in panel.status.text()
    assert w.export_payload()["resultados_observados"]["estado"] == "rascunho"
    json.dumps(w.export_payload(), allow_nan=False)
    panel.infer.setChecked(False)
    panel.analyze()
    assert panel.report["resumos"]["A"]["media"] == 1
    w.close()


def test_failed_observation_save_prevents_close_archive_and_new_planning(
    app, monkeypatch
):
    from PyQt6.QtWidgets import QTableWidgetItem

    w = PlannerWindow()
    w.show()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    w.percent_form.set_values(
        {"base": "m/v", "concentracao": 1, "quantidade_final": 100, "pureza": 100}
    )
    w.generate()
    record = w.history_id
    w.navigate(4)
    panel = w.analysis
    panel.unit.setText("mg/mL")
    panel.data.setItem(0, 0, QTableWidgetItem("Lote a preservar"))
    panel.data.setItem(0, 1, QTableWidgetItem("1;2;3"))
    real_save = w.history.save

    def fail(*args, **kwargs):
        raise OSError("Disco sem espaço (falha simulada)")

    monkeypatch.setattr(w.history, "save", fail)
    QTest.qWait(500)
    assert not w.close()
    assert w.isVisible()
    w.archive_record(record)
    assert w.history.list()[0]["id"] == record
    assert not list(w.history.archive_dir.glob("*.json"))
    w.new_planning()
    assert w.protocol.currentData() == "PREP-001" and w.history_id == record
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-002"))
    assert w.protocol.currentData() == "PREP-001"
    assert w.pending_export.isVisible()
    monkeypatch.setattr(w.history, "save", real_save)
    assert w.close()
    stored = json.loads(w.history.list()[0]["conteudo"])
    assert stored["resultados_observados"]["linhas_informadas"][0]["valores"] == "1;2;3"


def test_pending_snapshot_can_be_exported_after_plan_invalidated(
    app, tmp_path, monkeypatch
):
    from PyQt6.QtWidgets import QFileDialog, QTableWidgetItem

    w = PlannerWindow()
    w.show()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    w.percent_form.set_values(
        {"base": "m/v", "concentracao": 1, "quantidade_final": 100, "pureza": 100}
    )
    w.generate()
    w.navigate(4)
    panel = w.analysis
    panel.unit.setText("mg/mL")
    panel.data.setItem(0, 0, QTableWidgetItem("Medição ainda não salva"))
    panel.data.setItem(0, 1, QTableWidgetItem("1;2;3"))

    def fail(*args, **kwargs):
        raise OSError("Falha simulada ao gravar histórico")

    monkeypatch.setattr(w.history, "save", fail)
    QTest.qWait(500)
    w.percent_results.form.quantidade_final.setValue(0)
    assert w.plan is None and panel.context is None
    assert not w.close()
    assert (
        w.observation_pending[0]["resultados_observados"]["linhas_informadas"][0][
            "valores"
        ]
        == "1;2;3"
    )
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("", ""))
    w.export_pending()
    assert w.observation_pending is not None
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(tmp_path / "missing" / "backup.json"), ""),
    )
    w.export_pending()
    assert (
        w.observation_pending is not None
        and "continuam em memória" in w.history_status.text()
    )
    target = tmp_path / "backup.json"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: (str(target), ""))
    w.export_pending()
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["consulta_apenas"] is True
    assert data["experimento"]["parametros"]["quantidade_final"] == 100
    assert (
        data["experimento"]["resultados_observados"]["linhas_informadas"][0]["valores"]
        == "1;2;3"
    )
    assert w.observation_pending is None
    assert "histórico não foi atualizado" in w.history_status.text()
    assert w.close()


def test_committed_history_is_not_treated_as_unsaved_when_list_refresh_fails(
    app, monkeypatch
):
    from sqlalchemy.exc import SQLAlchemyError

    w = PlannerWindow()
    w.protocol.setCurrentIndex(w.protocol.findData("PREP-001"))
    w.complete_protocol()
    w.percent_form.set_values(
        {"base": "m/v", "concentracao": 1, "quantidade_final": 100, "pureza": 100}
    )

    def fail_refresh():
        raise SQLAlchemyError("Falha simulada na consulta da lista")

    monkeypatch.setattr(w, "refresh_history", fail_refresh)
    w.generate()
    record = w.history_id
    assert record is not None and w.observation_pending is None
    assert "Dados salvos" in w.history_status.text()
    assert len(w.history.list()) == 1
    assert w.save_history() is True and w.history_id == record
    assert len(w.history.list()) == 1
    assert w.close()


def test_catalog_reads_are_explicit_utf8_on_startup_and_formula(app, monkeypatch):
    from pathlib import Path

    from frontend.formulacao import FormulaForm

    original = Path.read_text
    reads = []

    def windows_default(path, *args, **kwargs):
        if path.name == "protocolos.json":
            reads.append(path)
            assert kwargs.get("encoding") == "utf-8", (
                "Leitura depende da codificação regional do Windows"
            )
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", windows_default)
    w = PlannerWindow()
    form = FormulaForm()
    assert len(w.catalog) == 10 and len(reads) >= 2
    form.close()
    w.close()


def test_packaged_app_check_checks_catalog_pop_and_observations(
    app, tmp_path, monkeypatch
):
    import subprocess
    import sys

    monkeypatch.setenv("PLANEJADOR_DATA_DIR", str(tmp_path / "before"))
    report = tmp_path / "smoke.json"
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from frontend.bundle_check import verify; sys.exit(verify(sys.argv[1]))",
            str(report),
        ],
        check=True,
        env={**os.environ, "PYTHONPATH": os.pathsep.join([".", "backend"])},
    )
    data = json.loads(report.read_text(encoding="utf-8"))
    assert "erro" not in data
    assert data["ok"] and data["protocolos"] == data["pops_exportados"] == 10
    assert data["massa_percentual_g"] == 9 and data["media_observada"] == 4
