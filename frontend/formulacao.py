"""Perguntas de formulação, com receita da fonte separada da autoria do pesquisador."""

import json
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class FormulaForm(QWidget):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.loading = False
        protocol = next(
            x
            for x in json.loads(
                Path(__file__).with_name("protocolos.json").read_text(encoding="utf-8")
            )
            if x["id"] == "PREP-008"
        )
        self.recipes = {x["id"]: x for x in protocol["formulacoes"]}
        layout = QVBoxLayout(self)
        self.mode = QComboBox()
        self.mode.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.mode.setMinimumContentsLength(15)
        for recipe in self.recipes.values():
            self.mode.addItem(recipe["nome"], recipe["id"])
        self.mode.addItem("Formulação do pesquisador", "pesquisador")
        form = QFormLayout()
        form.addRow("Qual formulação deseja usar?", self.mode)
        self.base, self.target = QDoubleSpinBox(), QDoubleSpinBox()
        for field in (self.base, self.target):
            field.setRange(0, 1000000000)
            field.setDecimals(6)
            field.setSuffix(" mL")
            field.setSpecialValueText("Informe o volume")
            field.valueChanged.connect(self.emit_change)
        form.addRow("Qual é o volume nominal de referência da receita (mL)?", self.base)
        form.addRow("Qual volume nominal deseja preparar (mL)?", self.target)
        self.source = QLineEdit()
        self.source.setMaxLength(2000)
        self.source.textChanged.connect(self.emit_change)
        form.addRow("Qual fonte/versão ou autoria fundamenta a receita?", self.source)
        layout.addLayout(form)
        component_question = QLabel(
            "Quais componentes e quantidades pertencem ao volume de referência?"
        )
        component_question.setWordWrap(True)
        layout.addWidget(component_question)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["Componente", "Quantidade\nna referência", "Unidade"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnWidth(1, 190)
        self.table.setColumnWidth(2, 90)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setMinimumHeight(250)
        self.table.itemChanged.connect(self.emit_change)
        layout.addWidget(self.table)
        actions = QHBoxLayout()
        self.add = QPushButton("Adicionar componente")
        self.remove = QPushButton("Remover componente")
        self.add.clicked.connect(lambda: self.add_component())
        self.remove.clicked.connect(self.remove_component)
        actions.addWidget(self.add)
        actions.addWidget(self.remove)
        layout.addLayout(actions)
        conditions = QFormLayout()
        self.ph, self.cycle, self.storage = QLineEdit(), QLineEdit(), QLineEdit()
        for question, field in [
            ("Qual pH e condição de medida foram definidos?", self.ph),
            (
                "Qual processo/ciclo de esterilização foi definido para este meio e esta carga?",
                self.cycle,
            ),
            (
                "Quais condições de conservação e validade foram definidas?",
                self.storage,
            ),
        ]:
            field.setMaxLength(2000)
            field.textChanged.connect(self.emit_change)
            conditions.addRow(question, field)
        self.procedure = QPlainTextEdit()
        self.procedure.setMaximumHeight(100)
        self.procedure.textChanged.connect(self.emit_change)
        conditions.addRow("Qual procedimento acompanha a formulação?", self.procedure)
        layout.addLayout(conditions)
        for grid in (form, conditions):
            for row in range(grid.rowCount()):
                label = grid.itemAt(row, QFormLayout.ItemRole.LabelRole).widget()
                label.setWordWrap(True)
                label.setFixedWidth(230)
        note = QLabel(
            "As quantidades são escaladas proporcionalmente, preservando as unidades. Água da receita não vira automaticamente q.s.p. ao volume final. Condições não informadas ficam pendentes. Selecionar outra formulação recarrega os ingredientes; a receita do pesquisador não é validada pela fonte do aplicativo."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        self.mode.currentIndexChanged.connect(self.load_recipe)
        self.load_recipe()

    def emit_change(self, *_):
        if not self.loading:
            self.changed.emit()

    def add_component(self, component=None):
        if self.table.rowCount() >= 100:
            return
        previous_loading = self.loading
        self.loading = True
        component = component or {}
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(component.get("nome", "")))
        amount = QDoubleSpinBox()
        amount.setDecimals(6)
        amount.setRange(0, 1000000000)
        amount.setSpecialValueText("Informe o valor")
        amount.setValue(component.get("quantidade", 0))
        unit = QComboBox()
        unit.addItems(["g", "mg", "mL", "µL"])
        unit.setCurrentText(component.get("unidade", "g"))
        amount.valueChanged.connect(self.emit_change)
        unit.currentIndexChanged.connect(self.emit_change)
        self.table.setCellWidget(row, 1, amount)
        self.table.setCellWidget(row, 2, unit)
        self.table.setRowHeight(
            row, max(48, amount.sizeHint().height() + 2, unit.sizeHint().height() + 2)
        )
        self.loading = previous_loading
        self.emit_change()

    def remove_component(self):
        if self.table.currentRow() >= 0:
            self.table.removeRow(self.table.currentRow())
            self.emit_change()

    def load_recipe(self, *_):
        self.loading = True
        recipe = self.recipes.get(self.mode.currentData())
        self.table.setRowCount(0)
        self.cycle.clear()
        self.storage.setText(recipe["conservacao"] if recipe else "")
        self.storage.setReadOnly(bool(recipe))
        self.base.setValue(recipe["volume_base_mL"] if recipe else 0)
        self.base.setReadOnly(bool(recipe))
        self.source.setText("Anvisa 2013, módulo 5, p. 15" if recipe else "")
        self.source.setReadOnly(bool(recipe))
        self.ph.setText(recipe["ph"] if recipe else "")
        self.ph.setReadOnly(bool(recipe))
        self.procedure.setPlainText(recipe["procedimento"] if recipe else "")
        self.procedure.setReadOnly(bool(recipe))
        for component in recipe["componentes"] if recipe else [{}]:
            self.add_component(component)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
            if recipe
            else QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )
        for row in range(self.table.rowCount()):
            for col in (1, 2):
                self.table.cellWidget(row, col).setEnabled(not recipe)
        self.add.setEnabled(not recipe)
        self.remove.setEnabled(not recipe)
        self.loading = False
        self.changed.emit()

    def values(self):
        return {
            "formulacao_id": self.mode.currentData(),
            "volume_base_mL": self.base.value(),
            "volume_alvo_mL": self.target.value(),
            "fonte_formula": self.source.text().strip(),
            "ph": self.ph.text().strip(),
            "ciclo": self.cycle.text().strip(),
            "conservacao": self.storage.text().strip(),
            "procedimento_formula": self.procedure.toPlainText().strip(),
            "componentes": [
                {
                    "nome": self.table.item(row, 0).text().strip(),
                    "quantidade": self.table.cellWidget(row, 1).value(),
                    "unidade": self.table.cellWidget(row, 2).currentText(),
                }
                for row in range(self.table.rowCount())
            ],
        }

    def set_values(self, values):
        self.blockSignals(True)
        self.mode.setCurrentIndex(
            self.mode.findData(values.get("formulacao_id", next(iter(self.recipes))))
        )
        self.load_recipe()
        self.target.setValue(values.get("volume_alvo_mL", 0))
        self.cycle.setText(values.get("ciclo", ""))
        if self.mode.currentData() == "pesquisador":
            self.storage.setText(values.get("conservacao", ""))
            self.base.setValue(values.get("volume_base_mL", 0))
            self.source.setText(values.get("fonte_formula", ""))
            self.ph.setText(values.get("ph", ""))
            self.procedure.setPlainText(values.get("procedimento_formula", ""))
            self.table.setRowCount(0)
            for component in values.get("componentes", [{}]):
                self.add_component(component)
        self.blockSignals(False)
        self.changed.emit()
