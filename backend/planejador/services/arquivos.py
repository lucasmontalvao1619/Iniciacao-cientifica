"""Gravação que preserva um arquivo anterior caso a exportação falhe."""

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def gravacao_atomica(destino):
    path = Path(destino)
    descriptor, temporary = tempfile.mkstemp(suffix=path.suffix, dir=path.parent)
    os.close(descriptor)
    temporary = Path(temporary)
    try:
        yield temporary
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
