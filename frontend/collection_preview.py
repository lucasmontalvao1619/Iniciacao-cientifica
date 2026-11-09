"""Consulta da coleta registrada, sem alterar amostras ou posições."""

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


def collection_dialog(collection, parent=None):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Organização da coleta")
    dialog.resize(850, 520)
    layout = QVBoxLayout(dialog)
    units = collection["unidades"]
    group_count = len({unit["grupo"] for unit in units})
    info = QLabel(
        f"{group_count} grupos · {len(units)} unidades. "
        "Posições sequenciais; o aplicativo não aplica randomização ou bloqueamento."
    )
    info.setWordWrap(True)
    layout.addWidget(info)
    selector = QComboBox()
    plates = sorted({u["placa"] for u in units if u.get("placa") is not None})
    for plate in plates:
        selector.addItem(f"Placa {plate}", plate)
    selector.setVisible(bool(plates))
    layout.addWidget(selector)
    table = QTableWidget()
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setWordWrap(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    layout.addWidget(table)

    def refresh():
        table.clear()
        if plates:
            selected = [u for u in units if u.get("placa") == selector.currentData()]
            geometry = collection.get("geometria")
            rows, cols = geometry or (
                max(ord(u["poco"][0]) - 64 for u in selected),
                max(int(u["poco"][1:]) for u in selected),
            )
            table.setRowCount(rows)
            table.setColumnCount(cols)
            table.setVerticalHeaderLabels([chr(65 + i) for i in range(rows)])
            table.setHorizontalHeaderLabels([str(i + 1) for i in range(cols)])
            for unit in selected:
                item = QTableWidgetItem(f"{unit['grupo']}\n{unit['amostra']}")
                item.setToolTip(
                    f"{unit['grupo']} · repetição {unit['repeticao']} · {unit['poco']}"
                )
                table.setItem(
                    ord(unit["poco"][0]) - 65, int(unit["poco"][1:]) - 1, item
                )
            table.verticalHeader().setDefaultSectionSize(64)
        else:
            table.setColumnCount(3)
            table.setRowCount(len(units))
            table.setHorizontalHeaderLabels(["Amostra", "Grupo", "Repetição"])
            for i, unit in enumerate(units):
                for j, key in enumerate(("amostra", "grupo", "repeticao")):
                    table.setItem(i, j, QTableWidgetItem(str(unit[key])))
        table.resizeColumnsToContents()

    selector.currentIndexChanged.connect(refresh)
    refresh()
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    buttons.button(QDialogButtonBox.StandardButton.Close).setText("Fechar")
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    return dialog
