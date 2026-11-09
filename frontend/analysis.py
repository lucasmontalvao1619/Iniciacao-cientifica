"""Entrada de medições, estatística do service e gráfico dos dados observados."""

import csv
import io
import json
import math
import textwrap
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, QRunnable, Qt, QThreadPool, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from frontend.numeric import DecimalSpinBox as QDoubleSpinBox
from planejador.core.exceptions import ErroPlanejamento


def parse_measurements(text):
    groups = {}
    for number, row in enumerate(csv.reader(io.StringIO(text), delimiter=";"), 1):
        if not row or not any(cell.strip() for cell in row):
            continue
        if number == 1 and [c.strip().lower() for c in row] == ["grupo", "valor"]:
            continue
        if len(row) != 2 or not row[0].strip():
            raise ValueError(f"Linha {number}: informe grupo;valor.")
        try:
            value = float(row[1].strip().replace(",", "."))
        except ValueError as exc:
            raise ValueError(f"Linha {number}: valor numérico inválido.") from exc
        if not math.isfinite(value):
            raise ValueError(f"Linha {number}: use um valor finito.")
        groups.setdefault(row[0].strip(), []).append(value)
    if not groups:
        raise ValueError("Insira pelo menos uma medição.")
    return groups


def calculate_report(groups, infer, alpha):
    from planejador.services import analisar_grupos

    if infer:
        report = analisar_grupos(groups, alpha=alpha)
    else:
        report = {
            "resumos": {
                name: analisar_grupos({name: values})["resumos"][name]
                for name, values in groups.items()
            },
            "teste_t": None,
            "anova": None,
        }
    try:
        json.dumps(report, allow_nan=False)
    except ValueError as exc:
        raise ValueError(
            "Resultado estatístico indefinido ou fora da faixa numérica. Revise os dados e os pressupostos; pode desativar a comparação para consultar o resumo descritivo."
        ) from exc
    return report


class AnalysisSignals(QObject):
    finished = pyqtSignal(object)


class AnalysisJob(QRunnable):
    def __init__(self, groups, infer, alpha, revision):
        super().__init__()
        self.groups, self.infer, self.alpha, self.revision = (
            groups,
            infer,
            alpha,
            revision,
        )
        self.signals = AnalysisSignals()

    def run(self):
        try:
            result = calculate_report(self.groups, self.infer, self.alpha)
            from frontend.plotting import load_figure

            load_figure()
        except Exception as exc:
            result = str(exc)
        self.signals.finished.emit((self.revision, self.groups, result))


class MeasurementsTable(QTableWidget):
    """Uma linha por grupo; colagem retangular como em uma planilha."""

    paste_requested = pyqtSignal()

    def __init__(self):
        super().__init__(2, 4)
        self.update_headers()
        self.paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.paste_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.paste_shortcut.activated.connect(self.paste_requested.emit)

    def update_headers(self):
        self.setHorizontalHeaderLabels(
            ["Grupo"] + [f"Medição {i}" for i in range(1, self.columnCount())]
        )

    def add_measurement(self):
        self.setColumnCount(self.columnCount() + 1)
        self.update_headers()

    def paste_cells(self):
        rows = list(
            csv.reader(io.StringIO(QApplication.clipboard().text()), delimiter="\t")
        )
        if not rows or not any(rows):
            return
        row, col = max(0, self.currentRow()), max(0, self.currentColumn())
        # Limite da entrada interativa; não alocar uma planilha inteira por engano.
        if len(rows) * max(map(len, rows), default=0) > 10000:
            raise ValueError("Cole até 10.000 células por vez.")
        self.blockSignals(True)
        try:
            self.setRowCount(max(self.rowCount(), row + len(rows)))
            self.setColumnCount(max(self.columnCount(), col + max(map(len, rows))))
            self.update_headers()
            for i, values in enumerate(rows):
                for j, value in enumerate(values):
                    self.setItem(row + i, col + j, QTableWidgetItem(value))
        finally:
            self.blockSignals(False)
        self.itemChanged.emit(self.item(row, col))


class AnalysisWidget(QWidget):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.report = None
        self.revision = 0
        self.worker = None
        self.import_worker = None
        self.import_source = None
        self.collection = None
        self.context = None
        self.plan_snapshot = None
        self.parameter_snapshot = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        title = QLabel("Medições e análise")
        self.heading = title
        font = title.font()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title.setWordWrap(True)
        layout.addWidget(title)
        self.context_label = QLabel(
            "Conclua o planejamento para registrar as medições."
        )
        self.context_label.setWordWrap(True)
        layout.addWidget(self.context_label)
        explanation = QLabel(
            "Uma linha por grupo, uma medição por célula. Ao colar do Excel, inclua os grupos na primeira coluna e omita o cabeçalho."
        )
        explanation.setWordWrap(True)
        self.entry = QGroupBox("Medições da bancada")
        entry = QVBoxLayout(self.entry)
        entry.setSpacing(12)
        layout.addWidget(self.entry)
        model = QPushButton("Organizar coleta e gerar modelo Excel")
        model.clicked.connect(self.export_collection_template)
        entry.addWidget(model)
        self.view_collection = QPushButton("Ver organização da coleta")
        self.view_collection.clicked.connect(self.show_collection)
        self.view_collection.setEnabled(False)
        entry.addWidget(self.view_collection)
        entry.addWidget(explanation)
        self.data = MeasurementsTable()
        self.data.paste_requested.connect(self.paste_measurements)
        self.data.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.data.setAccessibleName("Grupos e valores medidos")
        self.data.setMinimumHeight(128)
        self.data.setAlternatingRowColors(True)
        self.data.verticalHeader().setDefaultSectionSize(32)
        self.data.setMaximumHeight(160)
        entry.addWidget(self.data)
        controls = QHBoxLayout()
        add = QPushButton("Adicionar grupo")
        add.clicked.connect(lambda: self.data.insertRow(self.data.rowCount()))
        controls.addWidget(add)
        remove = QPushButton("Remover grupo selecionado")
        remove.clicked.connect(self.remove_group)
        controls.addWidget(remove)
        entry.addLayout(controls)
        paste_row = QHBoxLayout()
        paste = QPushButton("Colar do Excel")
        paste.clicked.connect(self.paste_measurements)
        import_button = QPushButton("Importar Excel (.xlsx)")
        import_button.setProperty("primary", True)
        import_button.clicked.connect(self.import_excel)
        paste_row.addWidget(import_button)
        paste_row.addWidget(paste)
        add_value = QPushButton("Adicionar medição")
        add_value.clicked.connect(self.data.add_measurement)
        paste_row.addWidget(add_value)
        entry.addLayout(paste_row)
        self.unit = QLineEdit()
        self.unit.setMaxLength(80)
        self.unit.setPlaceholderText("Ex.: absorbância, UFC/mL, mg/mL")
        unit_label = QLabel("Grandeza / unidade")
        unit_label.setWordWrap(True)
        unit_label.setBuddy(self.unit)
        unit_row = QHBoxLayout()
        unit_row.addWidget(unit_label)
        unit_row.addWidget(self.unit, 1)
        entry.addLayout(unit_row)
        self.run_button = QPushButton("Calcular resumo e gráfico")
        self.run_button.setMinimumHeight(42)
        self.run_button.setProperty("primary", True)
        self.run_button.clicked.connect(self.start_analysis)
        entry.addWidget(self.run_button)
        advanced_toggle = QCheckBox("Comparar grupos (opções avançadas)")
        layout.addWidget(advanced_toggle)
        self.advanced = QWidget()
        advanced_layout = QVBoxLayout(self.advanced)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        self.advanced.setVisible(False)
        advanced_toggle.toggled.connect(self.advanced.setVisible)
        self.infer = QCheckBox("Aplicar comparação estatística a grupos independentes")
        advanced_layout.addWidget(self.infer)
        design_label = QLabel(
            "As medições vêm de unidades experimentais independentes?"
        )
        design_label.setWordWrap(True)
        advanced_layout.addWidget(design_label)
        self.design = QComboBox()
        self.design.addItems(
            [
                "Não sei / ainda não conferi",
                "Sim, são independentes",
                "Não, são pareadas ou medidas repetidas",
            ]
        )
        advanced_layout.addWidget(self.design)
        design_help = QLabel(
            "Repetir a leitura do mesmo tubo não cria uma nova unidade independente. Dados pareados precisam de outra análise, ainda indisponível aqui."
        )
        design_help.setWordWrap(True)
        advanced_layout.addWidget(design_help)
        self.assumptions = QCheckBox("Os pressupostos do teste foram conferidos?")
        advanced_layout.addWidget(self.assumptions)
        self.alpha = QDoubleSpinBox()
        self.alpha.setRange(0.001, 0.999)
        self.alpha.setDecimals(3)
        self.alpha.setValue(0.05)
        self.alpha.setFixedWidth(110)
        alpha_row = QHBoxLayout()
        alpha_label = QLabel("Nível de significância (padrão: 0,05)")
        alpha_label.setBuddy(self.alpha)
        alpha_row.addWidget(alpha_label)
        alpha_row.addWidget(self.alpha)
        advanced_layout.addLayout(alpha_row)
        note = QLabel(
            "A comparação usa t de Student para dois grupos e ANOVA para três ou mais. É preciso avaliar se a distribuição dos dados e a dispersão entre grupos atendem ao teste (normalidade e homogeneidade de variâncias). Se não tiver certeza, mantenha apenas o resumo. O aplicativo não verifica esses pressupostos automaticamente."
        )
        note.setWordWrap(True)
        advanced_layout.addWidget(note)
        layout.addWidget(self.advanced)
        summary_heading = QLabel("Resumo estatístico")
        font = summary_heading.font()
        font.setPointSize(14)
        font.setBold(True)
        summary_heading.setFont(font)
        layout.addWidget(summary_heading)
        self.status = QLabel("Preencha a tabela para calcular seu primeiro resumo.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Grupo", "Medições", "Média", "Desvio padrão", "Variância"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.hide()
        layout.addWidget(self.table)
        self.figure = None
        self.canvas = None
        self.graph_page = QComboBox()
        self.graph_page.setAccessibleName("Página do gráfico por grupos")
        self.graph_page.currentIndexChanged.connect(self.draw_graph)
        self.graph_page.hide()
        layout.addWidget(self.graph_page)
        self.graph_groups = {}
        self.graph_layout = QVBoxLayout()
        layout.addLayout(self.graph_layout)
        self.save = QPushButton("Salvar gráfico em PNG")
        self.save.setEnabled(False)
        self.save.hide()
        self.save.clicked.connect(self.save_graph)
        layout.addWidget(self.save)
        self.data.itemChanged.connect(self.invalidate)
        self.unit.textChanged.connect(self.invalidate)
        self.save_experiment = QPushButton("Salvar planejamento e resultados em JSON")
        self.save_experiment.setEnabled(False)
        layout.addWidget(self.save_experiment)
        self.export_results = QPushButton(
            "Exportar dados e relatório (Excel, CSV ou Word)"
        )
        self.export_results.setEnabled(False)
        self.export_results.clicked.connect(self.export_observations)
        layout.addWidget(self.export_results)
        self.back = QPushButton("Voltar ao plano deste experimento")
        layout.addWidget(self.back)
        self.infer.toggled.connect(self.invalidate)
        self.alpha.valueChanged.connect(self.invalidate)
        self.design.currentIndexChanged.connect(self.invalidate)
        self.assumptions.toggled.connect(self.invalidate)

    def export_observations(self):
        payload = self.observation_payload()
        if payload is None or self.report is None:
            return
        path, selected_format = QFileDialog.getSaveFileName(
            self,
            "Exportar resultados",
            "resultados.xlsx",
            "Excel (*.xlsx);;Medições CSV (*.csv);;Resumo CSV (*.csv);;Relatório Word (*.docx)",
        )
        if not path:
            return
        try:
            from planejador.services.exportacao_resultados import exportar_resultados

            graph = None
            if Path(path).suffix.lower() == ".docx":
                graph = []
                selected_page = self.graph_page.currentIndex()
                try:
                    for page in range(self.graph_page.count()):
                        self.graph_page.setCurrentIndex(page)
                        image = io.BytesIO()
                        self.figure.savefig(image, format="png", dpi=140)
                        image.seek(0)
                        graph.append(image)
                finally:
                    self.graph_page.setCurrentIndex(selected_page)
            exportar_resultados(
                path,
                {
                    **payload,
                    "planejamento": self.plan_snapshot,
                    "parametros_planejados": self.parameter_snapshot,
                },
                resumo_csv=selected_format.startswith("Resumo CSV"),
                grafico=graph,
            )
            self.status.setText(f"Resultados exportados: {Path(path).name}")
        except (OSError, ValueError) as exc:
            self.status.setText(f"Não foi possível exportar: {exc}")

    def show_collection(self):
        if self.collection:
            from frontend.collection_preview import collection_dialog

            collection_dialog(self.collection, self).exec()

    def export_collection_template(self):
        from planejador.services.coleta import exportar_modelo, organizar_coleta

        if not self.unit.text().strip():
            self.status.setText(
                "Informe a grandeza/unidade a medir antes de organizar a coleta."
            )
            self.unit.setFocus()
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Organização da coleta")
        layout = QVBoxLayout(dialog)
        prompt = QLabel(
            "Quais grupos ou preparos serão medidos? Separe os nomes por ponto e vírgula."
        )
        prompt.setWordWrap(True)
        layout.addWidget(prompt)
        names = QLineEdit()
        names.setPlaceholderText("Nomes definidos no seu experimento")
        layout.addWidget(names)
        layout.addWidget(QLabel("Qual grupo é o controle? (opcional)"))
        control = QComboBox()

        def update_controls():
            previous = control.currentText()
            control.clear()
            control.addItem("Sem controle definido", None)
            for name in names.text().split(";"):
                if name.strip():
                    control.addItem(name.strip(), name.strip())
            index = control.findText(previous)
            if index >= 0:
                control.setCurrentIndex(index)

        names.textChanged.connect(update_controls)
        update_controls()
        layout.addWidget(control)
        layout.addWidget(QLabel("As repetições representam o quê?"))
        repetition_type = QComboBox()
        repetition_type.addItem("Ainda não definido", "indefinido")
        repetition_type.addItem("Unidades experimentais independentes", "independentes")
        repetition_type.addItem("Leituras repetidas da mesma unidade", "tecnicas")
        layout.addWidget(repetition_type)
        layout.addWidget(QLabel("Quantas repetições serão registradas por grupo?"))
        repeats = QSpinBox()
        repeats.setRange(1, 100)
        layout.addWidget(repeats)
        plate = QCheckBox("Organizar posições em microplacas")
        layout.addWidget(plate)
        geometry = QComboBox()
        for rows, cols in [(2, 3), (3, 4), (4, 6), (6, 8), (8, 12), (16, 24)]:
            geometry.addItem(f"{rows * cols} poços ({rows} × {cols})", (rows, cols))
        geometry.setCurrentIndex(4)
        geometry.setEnabled(False)
        plate.toggled.connect(geometry.setEnabled)
        layout.addWidget(geometry)
        if self.collection:
            names.setText("; ".join(g["nome"] for g in self.collection["grupos"]))
            units = self.collection["unidades"]
            repeats.setValue(max(u["repeticao"] for u in units))
            plate.setChecked(self.collection.get("microplaca", False))
            index = geometry.findData(tuple(self.collection.get("geometria", (8, 12))))
            geometry.setCurrentIndex(max(0, index))
            repetition_type.setCurrentIndex(
                max(0, repetition_type.findData(self.collection.get("tipo_repeticao")))
            )
            for group in self.collection["grupos"]:
                if group.get("papel") == "controle":
                    control.setCurrentIndex(control.findData(group["nome"]))
        note = QLabel(
            "Cada linha terá um identificador próprio. Repetições técnicas não são automaticamente tratadas como amostras independentes."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if not dialog.exec():
            return
        try:
            units = organizar_coleta(
                names.text().split(";"),
                repeats.value(),
                linhas=geometry.currentData()[0],
                colunas=geometry.currentData()[1],
                microplaca=plate.isChecked(),
            )
            path, _ = QFileDialog.getSaveFileName(
                self, "Salvar modelo de coleta", "coleta.xlsx", "Excel (*.xlsx)"
            )
            if not path:
                return
            collection = {
                "unidades": units,
                "unidade": self.unit.text().strip(),
                "microplaca": plate.isChecked(),
                "geometria": list(geometry.currentData()),
                "tipo_repeticao": repetition_type.currentData(),
                "grupos": [
                    {
                        "nome": name.strip(),
                        "papel": "controle"
                        if name.strip() == control.currentData()
                        else "tratamento ou preparo",
                    }
                    for name in names.text().split(";")
                ],
            }
            exportar_modelo(
                path, units, {**self.context, "coleta": collection}, self.unit.text()
            )
            self.collection = collection
            self.view_collection.setEnabled(True)
            self.invalidate()
            self.status.setText(
                f"Modelo salvo: {len(units)} unidades de coleta, com medições ainda vazias. Preencha os valores e importe o arquivo."
            )
        except (ValueError, OSError) as exc:
            self.status.setText(f"Não foi possível gerar o modelo: {exc}")

    def import_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar medições", "", "Excel (*.xlsx)"
        )
        if not path:
            return
        from frontend.excel_import import ImportJob

        if self.import_worker is not None:
            self.status.setText("Uma importação já está em andamento.")
            return
        self.status.setText("Lendo a planilha… A janela continua disponível.")
        self.import_worker = ImportJob(path, self.revision)
        self.import_worker.signals.finished.connect(self.finish_import)
        QThreadPool.globalInstance().start(self.import_worker)

    def finish_import(self, outcome):
        path, revision, sheets, digest = outcome
        self.import_worker = None
        if revision != self.revision:
            self.status.setText(
                "O experimento mudou durante a leitura. Importe novamente para conferir os dados atuais."
            )
            return
        try:
            from frontend.excel_import import ExcelPreview

            if isinstance(sheets, str):
                raise ValueError(sheets)
            from planejador.services.coleta import conferir_coleta

            collection = conferir_coleta(sheets, self.context)
            preview = ExcelPreview(
                {k: v for k, v in sheets.items() if k != "Planejamento"}, self
            )
            if not preview.exec():
                return
            groups = preview.groups
            reference_collection = collection or self.collection
            if reference_collection is not None:
                expected = {}
                for unit in reference_collection["unidades"]:
                    expected[unit["grupo"]] = expected.get(unit["grupo"], 0) + 1
                if {name: len(values) for name, values in groups.items()} != expected:
                    raise ValueError(
                        "Os grupos ou números de medições diferem da coleta planejada. Confira a planilha ou atualize a organização da coleta."
                    )
            self.data.blockSignals(True)
            try:
                self.data.clearContents()
                self.data.setRowCount(len(groups))
                self.data.setColumnCount(min(40, max(map(len, groups.values()))) + 1)
                self.data.update_headers()
                for row, (name, values) in enumerate(groups.items()):
                    self.data.setItem(row, 0, QTableWidgetItem(name))
                    cells = (
                        values if len(values) <= 40 else [";".join(map(str, values))]
                    )
                    for col, value in enumerate(cells, 1):
                        self.data.setItem(row, col, QTableWidgetItem(str(value)))
            finally:
                self.data.blockSignals(False)
            if collection is not None:
                self.collection = collection
                self.view_collection.setEnabled(True)
                self.unit.setText(collection["unidade"])
            self.import_source = {
                "arquivo": Path(path).name,
                "importado_em": datetime.now()
                .astimezone()
                .isoformat(timespec="seconds"),
                "sha256": digest,
                "aba": preview.sheet.currentText(),
                "formato": preview.mode.currentData(),
                "mapeamento": preview.mapping,
            }
            self.invalidate()
            self.status.setText(
                f"{Path(path).name}: grupos e medições importados. Confira a grandeza/unidade e calcule o resumo."
            )
        except Exception as exc:
            self.status.setText(f"Não foi possível importar: {exc}")

    def paste_measurements(self):
        try:
            self.data.paste_cells()
        except ValueError as exc:
            self.status.setText(str(exc))

    def remove_group(self):
        row = self.data.currentRow()
        if row >= 0:
            self.data.removeRow(row)
            self.invalidate()

    def clear_experiment(self):
        self.collection = None
        self.view_collection.setEnabled(False)
        self.import_source = None
        self.context = None
        self.data.clearContents()
        self.data.setRowCount(2)
        self.data.setColumnCount(4)
        self.data.update_headers()
        self.design.setCurrentIndex(0)
        self.assumptions.setChecked(False)
        self.unit.clear()
        self.infer.setChecked(False)
        self.alpha.setValue(0.05)
        self.context_label.setText("Conclua o planejamento para registrar as medições.")
        self.invalidate()

    def set_experiment(self, title, plan, record_id=None, parameters=None):
        self.clear_experiment()
        import copy
        import hashlib

        self.plan_snapshot = copy.deepcopy(plan)
        self.parameter_snapshot = copy.deepcopy(parameters or {})
        self.context = {
            "titulo": title,
            "protocolo": plan["protocolo"],
            "registro_id": record_id,
            "planejamento_sha256": hashlib.sha256(
                json.dumps(
                    plan, sort_keys=True, ensure_ascii=False, allow_nan=False
                ).encode()
            ).hexdigest(),
        }
        if "protocolo_id" in plan:
            self.context["protocolo_id"] = plan["protocolo_id"]
        detail = ""
        if "n_amostras" in plan:
            self.context.update(
                amostras=plan["n_amostras"],
                replicatas=plan["n_replicatas"],
                controles=plan["n_controles"],
            )
            detail = f"Planejado · Amostras: {plan['n_amostras']} · Repetições por amostra: {plan['n_replicatas']} · Controles: {plan['n_controles']}. "
        heading = (
            title if title == plan["protocolo"] else f"{title} · {plan['protocolo']}"
        )
        self.context_label.setText(
            f"{heading}\n{detail}Medições vinculadas a este planejamento, separadas dos valores calculados."
        )
        self.status.setText(
            "Preencha os grupos e valores obtidos na bancada. Nenhuma medição é preenchida automaticamente."
        )

    def restore_observations(self, saved):
        self.blockSignals(True)
        self.data.blockSignals(True)
        try:
            rows = saved.get("linhas_informadas", [])
            self.data.clearContents()
            self.data.setRowCount(max(2, len(rows)))
            self.data.setColumnCount(4)
            self.data.update_headers()
            for row, record in enumerate(rows):
                self.data.setItem(row, 0, QTableWidgetItem(record.get("grupo", "")))
                self.data.setItem(row, 1, QTableWidgetItem(record.get("valores", "")))
            self.unit.setText(saved.get("unidade", ""))
            self.infer.setChecked(saved.get("comparacao_solicitada", False))
            self.alpha.setValue(saved.get("alpha", 0.05))
            self.design.setCurrentIndex(
                max(0, self.design.findText(saved.get("desenho_informado", "")))
            )
            self.assumptions.setChecked(saved.get("pressupostos_conferidos", False))
            self.collection = saved.get("coleta_planejada")
            self.view_collection.setEnabled(bool(self.collection))
            self.import_source = saved.get("importacao")
            self.invalidate()
        finally:
            self.data.blockSignals(False)
            self.blockSignals(False)
        self.status.setText(
            "Planejamento e medições restaurados. Calcule o resumo para conferir a análise nesta versão."
        )

    def observation_payload(self):
        if self.context is None:
            return None
        rows = [
            {
                "grupo": self.data.item(row, 0).text()
                if self.data.item(row, 0)
                else "",
                "valores": ";".join(
                    self.data.item(row, col).text()
                    for col in range(1, self.data.columnCount())
                    if self.data.item(row, col)
                    and self.data.item(row, col).text().strip()
                ),
            }
            for row in range(self.data.rowCount())
        ]
        rows = [row for row in rows if row["grupo"] or row["valores"]]
        if not rows and not self.unit.text().strip():
            return None
        from planejador import __version__

        payload = {
            "versao_aplicativo": __version__,
            "linhas_informadas": rows,
            "unidade": self.unit.text().strip(),
            "comparacao_solicitada": self.infer.isChecked(),
            "alpha": self.alpha.value(),
            "desenho_informado": self.design.currentText(),
            "pressupostos_conferidos": self.assumptions.isChecked(),
            "estado": "analisado" if self.report is not None else "rascunho",
        }
        if self.collection is not None:
            payload["coleta_planejada"] = self.collection
        if self.import_source is not None:
            payload["importacao"] = dict(self.import_source)
        if self.report is not None:
            payload.update(medicoes=self.read_groups(), analise=self.report)
        return payload

    def read_groups(self):
        stream = io.StringIO()
        writer = csv.writer(stream, delimiter=";")
        names = set()
        for row in range(self.data.rowCount()):
            name = (
                self.data.item(row, 0).text().strip() if self.data.item(row, 0) else ""
            )
            values = ";".join(
                self.data.item(row, col).text().strip()
                for col in range(1, self.data.columnCount())
                if self.data.item(row, col) and self.data.item(row, col).text().strip()
            )
            if not name and not values:
                continue
            if not name or not values:
                self.data.setCurrentCell(row, 0 if not name else 1)
                self.data.setFocus()
                raise ValueError(
                    f"Linha {row + 1}: preencha o nome do grupo e seus valores."
                )
            if name.casefold() in names:
                raise ValueError(
                    f"Grupo repetido: {name}. Reúna os valores na mesma linha."
                )
            names.add(name.casefold())
            for value in values.split(";"):
                writer.writerow([name, value])
        return parse_measurements(stream.getvalue())

    def invalidate(self, *_):
        self.revision += 1
        self.report = None
        self.table.setRowCount(0)
        self.table.hide()
        self.graph_page.hide()
        self.graph_groups = {}
        self.save.hide()
        if self.figure is not None and self.figure.axes:
            self.figure.clear()
            self.canvas.hide()
        self.save.setEnabled(False)
        self.save_experiment.setEnabled(False)
        self.export_results.setEnabled(False)
        self.status.setText(
            "Informe suas medições e clique em Calcular resumo e gráfico."
        )

        if self.context is not None:
            self.changed.emit()

    def analysis_input(self):
        if self.context is None:
            raise ValueError("Conclua o planejamento antes de analisar.")
        if not self.unit.text().strip():
            self.unit.setFocus()
            raise ValueError(
                "Informe o que foi medido ou a unidade para identificar o gráfico."
            )
        groups = self.read_groups()
        if self.collection:
            expected = {}
            for unit in self.collection["unidades"]:
                expected[unit["grupo"]] = expected.get(unit["grupo"], 0) + 1
            if {name: len(values) for name, values in groups.items()} != expected:
                raise ValueError(
                    "Grupos ou quantidades de medições diferem da coleta planejada. Confira a organização da coleta e os dados."
                )
        if self.infer.isChecked():
            if self.collection and self.collection.get("tipo_repeticao") == "tecnicas":
                raise ValueError(
                    "A coleta registra leituras repetidas da mesma unidade. Use o resumo descritivo; elas não são amostras independentes para t/ANOVA."
                )
            if self.design.currentIndex() != 1:
                raise ValueError(
                    "Confirme unidades independentes para comparar. Para dados pareados ou dúvida, desative a comparação e consulte o resumo."
                )
            if not self.assumptions.isChecked():
                raise ValueError(
                    "Confira os pressupostos antes de comparar; enquanto isso, desative a comparação para ver o resumo e o gráfico."
                )
        return groups

    def start_analysis(self):
        self.invalidate()
        try:
            groups = self.analysis_input()
        except (ValueError, ErroPlanejamento) as exc:
            self.status.setText(f"Não foi possível analisar: {exc}")
            return
        self.run_button.setEnabled(False)
        self.status.setText(
            "Calculando resumo e gráfico… Você pode continuar usando a janela."
        )
        self.worker = AnalysisJob(
            groups, self.infer.isChecked(), self.alpha.value(), self.revision
        )
        self.worker.signals.finished.connect(self.finish_analysis)
        QThreadPool.globalInstance().start(self.worker)

    def finish_analysis(self, outcome):
        revision, groups, result = outcome
        self.worker = None
        self.run_button.setEnabled(True)
        if revision != self.revision:
            self.status.setText(
                "Os dados mudaram durante o cálculo. Clique em Calcular resumo e gráfico para analisar os valores atuais."
            )
            return
        if isinstance(result, str):
            self.status.setText(f"Não foi possível analisar: {result}")
            return
        self.report = result
        self.render_analysis(groups)

    def analyze(self):
        self.invalidate()
        try:
            groups = self.analysis_input()
            self.report = calculate_report(
                groups, self.infer.isChecked(), self.alpha.value()
            )
        except (ValueError, ErroPlanejamento) as exc:
            self.report = None
            self.status.setText(f"Não foi possível analisar: {exc}")
            return
        self.render_analysis(groups)

    def render_analysis(self, groups):
        self.table.setRowCount(len(groups))
        self.table.setFixedHeight(
            min(
                240,
                max(94, self.table.horizontalHeader().height() + 32 * len(groups) + 4),
            )
        )
        self.table.show()
        for i, (name, summary) in enumerate(self.report["resumos"].items()):
            for j, value in enumerate(
                [
                    name,
                    summary["n"],
                    summary["media"],
                    summary["desvio_padrao"],
                    summary["variancia"],
                ]
            ):
                text = (
                    f"{value:.5g}"
                    if isinstance(value, float) and math.isfinite(value)
                    else str(value)
                )
                if isinstance(value, float) and not math.isfinite(value):
                    text = "não definido"
                self.table.setItem(i, j, QTableWidgetItem(text))
        if self.figure is None:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

            from frontend.plotting import load_figure

            self.figure = load_figure()(figsize=(6, 3.8), layout="constrained")
            self.canvas = FigureCanvasQTAgg(self.figure)
            self.canvas.setMinimumHeight(360)
            self.graph_layout.addWidget(self.canvas)
        self.graph_groups = groups
        self.graph_page.blockSignals(True)
        self.graph_page.clear()
        for start in range(0, len(groups), 8):
            self.graph_page.addItem(
                f"Gráfico · grupos {start + 1} a {min(start + 8, len(groups))} de {len(groups)}"
            )
        self.graph_page.blockSignals(False)
        self.graph_page.setVisible(len(groups) > 8)
        self.draw_graph()
        test = self.report.get("teste_t") or self.report.get("anova")
        if test:
            kind = "t de Student" if self.report.get("teste_t") else "ANOVA de uma via"
            self.status.setText(
                f"{kind}: p = {test['valor_p']:.5g}; α = {self.alpha.value():.3g}. Interprete junto dos pressupostos e do desenho experimental."
            )
        else:
            self.status.setText(
                "Resumo calculado. A média indica o valor central; o desvio padrão, a dispersão. Nenhuma comparação entre grupos foi aplicada."
            )
        self.report["experimento"] = dict(self.context)
        self.report["unidade"] = self.unit.text().strip()
        self.save.setEnabled(True)
        self.save.show()
        self.save_experiment.setEnabled(True)
        self.export_results.setEnabled(True)
        self.changed.emit()
        parent = self.parentWidget()
        while parent is not None:
            if isinstance(parent, QScrollArea):
                parent.ensureWidgetVisible(self.table, 0, 24)
                break
            parent = parent.parentWidget()

    def draw_graph(self, *_):
        if self.figure is None or self.report is None or not self.graph_groups:
            return
        self.figure.clear()
        axes = self.figure.add_subplot()
        start = max(0, self.graph_page.currentIndex()) * 8
        groups = dict(list(self.graph_groups.items())[start : start + 8])
        for i, (name, values) in enumerate(groups.items()):
            offsets = [
                i - 0.18 + 0.12 * j / max(1, len(values) - 1)
                for j in range(len(values))
            ]
            axes.scatter(
                offsets, values, alpha=0.75, label="Medições" if i == 0 else None
            )
            summary = self.report["resumos"][name]
            axes.errorbar(
                i,
                summary["media"],
                yerr=summary["desvio_padrao"],
                fmt="D",
                color="black",
                capsize=5,
                label="Média ± desvio padrão" if i == 0 else None,
            )
        axes.legend(fontsize="small")
        axes.set_xticks(
            range(len(groups)), [textwrap.fill(name, 20) for name in groups]
        )
        axes.set_ylabel(self.unit.text().strip(), wrap=True)
        title = self.context["titulo"]
        if len(self.graph_groups) > 8:
            title += f" (grupos {start + 1} a {start + len(groups)} de {len(self.graph_groups)})"
        axes.set_title(textwrap.fill(title, 60), wrap=True)
        axes.set_xlabel("Grupo")
        axes.grid(axis="y", alpha=0.2)
        self.canvas.show()
        self.canvas.draw_idle()

    def save_graph(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar página atual do gráfico", "grafico.png", "PNG (*.png)"
        )
        if path:
            try:
                self.figure.savefig(Path(path), dpi=160)
            except OSError as exc:
                self.status.setText(f"Falha ao salvar: {exc}")
