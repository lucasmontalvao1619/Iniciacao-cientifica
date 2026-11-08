"""Perguntas ao pesquisador para a instrução de um meio comercial."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QWidget,
)

from frontend.numeric import DecimalSpinBox as QDoubleSpinBox


class MeioComercialForm(QWidget):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        form = QFormLayout(self)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form.setVerticalSpacing(12)
        self.name = QLineEdit()
        self.name.setMaxLength(160)
        form.addRow("Qual é o meio/produto? (opcional)", self.name)
        self.name.textChanged.connect(self.changed)
        self.fields = {}
        for key, question, suffix in [
            ("massa_referencia_g", "Qual massa de pó a instrução recomenda (g)?", " g"),
            (
                "volume_referencia_mL",
                "Para qual volume a instrução recomenda essa massa (mL)?",
                " mL",
            ),
            ("volume_alvo_mL", "Qual volume desse tipo deseja preparar (mL)?", " mL"),
        ]:
            field = QDoubleSpinBox()
            field.setRange(0, 1000000000)
            field.setDecimals(6)
            field.setSuffix(suffix)
            field.setSpecialValueText("Informe o valor")
            field.valueChanged.connect(self.changed)
            self.fields[key] = field
            form.addRow(question, field)
        self.volume_type = QComboBox()
        self.volume_type.addItem("Selecione conforme a instrução", None)
        self.volume_type.addItem("Volume de água", "agua")
        self.volume_type.addItem("Volume final (q.s.p.)", "final")
        self.volume_type.currentIndexChanged.connect(self.changed)
        self.volume_type.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.volume_type.setMinimumContentsLength(15)
        form.addRow("A instrução se refere a água ou volume final?", self.volume_type)
        self.texts = {}
        for key, question in [
            (
                "referencia_fabricante",
                "Qual rótulo/documento e versão fundamentam a proporção?",
            ),
            (
                "consulta_fabricante",
                "Quando consultou essa instrução? (data, hora e fuso, se conhecidos)",
            ),
            ("ph", "Qual pH e condição de medida se aplicam?"),
            ("ciclo", "Qual processo/ciclo de esterilização se aplica?"),
            (
                "suplementos",
                "Quais suplementos/adições são exigidos? (ou nenhum, conforme instrução)",
            ),
            ("conservacao", "Quais condições de conservação/validade se aplicam?"),
        ]:
            field = QLineEdit()
            field.setMaxLength(2000)
            field.textChanged.connect(self.changed)
            self.texts[key] = field
            form.addRow(question, field)
        self.procedure = QPlainTextEdit()
        self.procedure.setMaximumHeight(100)
        self.procedure.textChanged.connect(self.changed)
        form.addRow(
            "Qual procedimento de hidratação/preparo acompanha o produto?",
            self.procedure,
        )
        note = QLabel(
            "Os números devem reproduzir a instrução do produto: 1 L corresponde a 1000 mL. Não suponha que volume de água e volume final sejam iguais. A referência e a consulta do fabricante são declaradas pelo pesquisador; não são verificadas automaticamente. Campos de preparo ausentes ficam pendentes, sem ciclo ou validade universais."
        )
        note.setWordWrap(True)
        self.note = note
        form.addRow(note)
        for row in range(form.rowCount()):
            label = form.itemAt(row, QFormLayout.ItemRole.LabelRole)
            if label and isinstance(label.widget(), QLabel):
                label.widget().setWordWrap(True)
                label.widget().setFixedWidth(230)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        margins = self.layout().contentsMargins()
        self.note.setMinimumHeight(
            self.note.heightForWidth(
                max(1, self.width() - margins.left() - margins.right())
            )
        )

    def values(self):
        return {
            "soluto": self.name.text().strip(),
            **{key: field.value() for key, field in self.fields.items()},
            "tipo_volume": self.volume_type.currentData(),
            **{key: field.text().strip() for key, field in self.texts.items()},
            "procedimento_fabricante": self.procedure.toPlainText().strip(),
        }

    def set_values(self, values):
        self.blockSignals(True)
        self.name.setText(values.get("soluto", ""))
        for key, field in self.fields.items():
            field.setValue(values.get(key, 0))
        for key, field in self.texts.items():
            field.setText(values.get(key, ""))
        self.volume_type.setCurrentIndex(
            self.volume_type.findData(values.get("tipo_volume"))
        )
        self.procedure.setPlainText(values.get("procedimento_fabricante", ""))
        self.blockSignals(False)
        self.changed.emit()
