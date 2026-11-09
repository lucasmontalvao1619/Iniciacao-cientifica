"""Prévia de importação: nenhuma medição é aplicada antes da conferência."""

from PyQt6.QtCore import QObject, QRunnable, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
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
        intro = QLabel(
            "Confira a aba, a organização e os grupos reconhecidos antes de substituir a tabela atual."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
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
        layout.addWidget(QLabel("Linha do cabeçalho"))
        self.header_row = QSpinBox()
        self.header_row.setRange(1, max(map(len, sheets.values())))
        layout.addWidget(self.header_row)
        self.group_column = QComboBox()
        self.value_column = QComboBox()
        self.columns = QListWidget()
        self.columns.setMaximumHeight(110)
        layout.addWidget(self.group_column)
        layout.addWidget(self.value_column)
        layout.addWidget(self.columns)
        self.mapping = {}
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
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.sheet.currentIndexChanged.connect(self.rebuild_mapping)
        self.header_row.valueChanged.connect(self.rebuild_mapping)
        self.mode.currentIndexChanged.connect(self.refresh)
        self.group_column.currentIndexChanged.connect(self.refresh)
        self.value_column.currentIndexChanged.connect(self.refresh)
        self.columns.itemChanged.connect(self.refresh)
        self.rebuild_mapping()

    def rebuild_mapping(self):
        rows = self.sheets[self.sheet.currentText()]
        index = self.header_row.value() - 1
        header = rows[index] if index < len(rows) else []
        for widget in (self.group_column, self.value_column, self.columns):
            widget.blockSignals(True)
            widget.clear()
        self.group_column.addItem("Coluna do grupo: reconhecer", None)
        self.value_column.addItem("Coluna da medição: reconhecer", None)
        from planejador.services.importacao_excel import normalized

        for i, name in enumerate(header):
            self.group_column.addItem(f"Grupo: {name}", i)
            self.value_column.addItem(f"Medição: {name}", i)
            item = QListWidgetItem(f"{i + 1}: {name}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Unchecked
                if normalized(name)
                in {
                    "amostra",
                    "id",
                    "identificador",
                    "placa",
                    "poco",
                    "replica",
                    "repeticao",
                    "unidade",
                }
                else Qt.CheckState.Checked
            )
            self.columns.addItem(item)
        for widget in (self.group_column, self.value_column, self.columns):
            widget.blockSignals(False)
        self.refresh()

    def refresh(self):
        self.groups = None
        self.table.clear()
        self.table.setRowCount(0)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        selected = self.mode.currentData()
        self.group_column.setVisible(selected == "long")
        self.value_column.setVisible(selected == "long")
        self.columns.setVisible(selected == "columns")
        self.mapping = {
            "header_row": self.header_row.value() - 1,
            "group_column": self.group_column.currentData(),
            "value_column": self.value_column.currentData(),
            "columns": [
                i
                for i in range(self.columns.count())
                if self.columns.item(i).checkState() == Qt.CheckState.Checked
            ]
            if selected == "columns"
            else None,
        }
        try:
            mode, groups = recognize(
                self.sheets[self.sheet.currentText()], selected, **self.mapping
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
            with Path(self.path).open("rb") as source:
                content = source.read(20 * 1024 * 1024 + 1)
            result = read_workbook(self.path, content=content)
            digest = hashlib.sha256(content).hexdigest()
        except Exception as exc:
            result, digest = str(exc), None
        self.signals.finished.emit((self.path, self.revision, result, digest))
