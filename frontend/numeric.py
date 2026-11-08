"""Campos Qt com digitação direta, sem alterar limites nem unidades."""

from PyQt6.QtCore import QLocale
from PyQt6.QtWidgets import QDoubleSpinBox, QLineEdit, QSpinBox


class _NumericEdit(QLineEdit):
    def select_hint(self):
        hint = self.parent().specialValueText()
        if hint and self.text() == hint:
            self.selectAll()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.select_hint()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.select_hint()


class DecimalSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLocale(QLocale.c())
        self.setLineEdit(_NumericEdit(self))
        # Digitar vários algarismos não deve redesenhar e salvar a cada tecla.
        self.setKeyboardTracking(False)
        self.setToolTip(
            "Digite o número com ponto ou vírgula decimal, sem separador de milhar. Confirme com Enter ou ao sair do campo."
        )

    def validate(self, text, position):
        return super().validate(text.replace(",", "."), position)

    def valueFromText(self, text):
        return super().valueFromText(text.replace(",", "."))


class IntegerSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLocale(QLocale.c())
        self.setLineEdit(_NumericEdit(self))
        self.setKeyboardTracking(False)
