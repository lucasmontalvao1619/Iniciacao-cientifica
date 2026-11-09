"""Cache de fontes estável e carregamento sem bloquear a janela Qt."""

import hashlib
import logging
import os
import sys
from pathlib import Path

from PyQt6.QtCore import QObject, QRunnable, QStandardPaths, pyqtSignal

figure_ready = False


def configure_cache():
    if not getattr(sys, "frozen", False):
        return
    # PyInstaller usa cache temporário por execução; nossos bundles são onedir.
    installation = hashlib.sha256(
        str(Path(sys._MEIPASS).resolve()).encode()
    ).hexdigest()[:12]
    base = Path(
        os.environ.get("PLANEJADOR_DATA_DIR")
        or QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.CacheLocation
        )
    )
    cache = base / "fontes-graficos" / installation
    try:
        cache.mkdir(parents=True, exist_ok=True)
    except OSError:
        logging.warning("Cache de fontes indisponível; usando cache temporário.")
        return
    os.environ["MPLCONFIGDIR"] = str(cache)


def load_figure():
    global figure_ready
    from matplotlib.figure import Figure

    figure_ready = True
    return Figure


class FontSignals(QObject):
    finished = pyqtSignal(str)


class FontJob(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = FontSignals()

    def run(self):
        try:
            load_figure()
            error = ""
        except Exception as exc:
            error = str(exc)
        self.signals.finished.emit(error)
