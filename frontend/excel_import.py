"""Prévia de importação: nenhuma medição é aplicada antes da conferência."""

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from planejador.services.importacao_excel import recognize


class ExcelPreview(QDialog):
    def __init__(self, sheets, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importar medições do Excel")
        self.resize(720, 520)
        self.sheets = sheets
        self.groups = None
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Confira a aba, a organização e os grupos reconhecidos antes de substituir a tabela atual."
            )
        )
        self.sheet = QComboBox()
        self.sheet.addItems(sheets)
        layout.addWidget(self.sheet)
        self.mode = QComboBox()
        for title, key in [
            ("Reconhecer automaticamente", "auto"),
            ("Uma coluna por grupo", "columns"),
            ("Uma linha por grupo", "rows"),
            ("Uma linha por observação (Grupo e Valor)", "long"),
        ]:
            self.mode.addItem(title, key)
        layout.addWidget(self.mode)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(
            "Importar grupos e medições"
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.sheet.currentIndexChanged.connect(self.refresh)
        self.mode.currentIndexChanged.connect(self.refresh)
        self.refresh()

    def refresh(self):
        self.groups = None
        self.table.clear()
        self.table.setRowCount(0)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        try:
            mode, groups = recognize(
                self.sheets[self.sheet.currentText()], self.mode.currentData()
            )
        except ValueError as exc:
            self.status.setText(str(exc))
            return
        self.groups = groups
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Grupo", "Medições", "Primeiros valores"])
        self.table.setRowCount(len(groups))
        for row, (name, values) in enumerate(groups.items()):
            for col, text in enumerate(
                [name, str(len(values)), "; ".join(f"{v:g}" for v in values[:6])]
            ):
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.status.setText(
            f"{len(groups)} grupos, {sum(map(len, groups.values()))} medições. Campos vazios em colunas/linhas foram ignorados; nenhum valor foi preenchido automaticamente."
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)


class ImportSignals(QObject):
    finished = pyqtSignal(object)


class ImportJob(QRunnable):
    def __init__(self, path, revision):
        super().__init__()
        self.path, self.revision = path, revision
        self.signals = ImportSignals()

    def run(self):
        import hashlib
        from pathlib import Path

        from planejador.services.importacao_excel import read_workbook

        try:
            result = read_workbook(self.path)
            digest = hashlib.sha256(Path(self.path).read_bytes()).hexdigest()
        except Exception as exc:
            result, digest = str(exc), None
        self.signals.finished.emit((self.path, self.revision, result, digest))
