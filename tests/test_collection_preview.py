from PyQt6.QtWidgets import QComboBox, QTableWidget

from frontend.app import create_app
from frontend.collection_preview import collection_dialog
from planejador.services.coleta import organizar_coleta


def test_plate_preview_keeps_geometry_and_switches_plates():
    app = create_app()
    units = organizar_coleta(["Controle", "Tratamento"], 50, microplaca=True)
    collection = {
        "unidades": units,
        "grupos": [{"nome": "Controle"}, {"nome": "Tratamento"}],
        "geometria": [8, 12],
    }
    dialog = collection_dialog(collection)
    table = dialog.findChild(QTableWidget)
    selector = dialog.findChild(QComboBox)
    assert (table.rowCount(), table.columnCount()) == (8, 12)
    assert table.item(0, 0).text() == "Controle\nU00001"
    selector.setCurrentIndex(1)
    app.processEvents()
    assert table.item(0, 0).text() == "Tratamento\nU00097"
    assert table.item(0, 4) is None
    dialog.close()
