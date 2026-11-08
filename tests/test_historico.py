import json
from pathlib import Path

import pytest

from planejador.services.historico import Historico


def test_limit_restart_archive_and_update(tmp_path):
    store = Historico(tmp_path)
    first = store.save(
        {
            "titulo": "Primeiro",
            "plano": {"resultado": 9},
            "parametros": {"quantidade": 1000},
        }
    )
    store.save({"titulo": "Recalculado", "plano": {"resultado": 4.5}}, first)
    assert len(store.list()) == 1
    for i in range(10):
        store.save({"titulo": f"Experimento {i}", "dados": [i]})
    assert len(store.list()) == 10
    files = list(store.archive_dir.glob("*.json"))
    assert len(files) == 1
    archived = json.loads(files[0].read_text(encoding="utf-8"))
    assert (
        archived["consulta_apenas"]
        and archived["experimento"]["plano"]["resultado"] == 4.5
    )
    reopened = Historico(tmp_path)
    assert len(reopened.list()) == 10
    target = reopened.archive(reopened.list()[0]["id"])
    assert target.exists() and len(reopened.list()) == 9


def test_archive_failure_keeps_record(tmp_path, monkeypatch):
    store = Historico(tmp_path)
    record_id = store.save({"titulo": "Preservar"})
    write_text = Path.write_text

    def fail_archive(path, *args, **kwargs):
        if path.suffix == ".tmp":
            raise OSError("Sem espaço")
        return write_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_archive)
    with pytest.raises(OSError):
        store.archive(record_id)
    assert store.list()[0]["id"] == record_id


def test_save_reconnects_when_sqlite_directory_was_moved(tmp_path):
    import sys

    if sys.platform == "win32":
        pytest.skip("Windows impede mover diretório com SQLite aberto")
    original = tmp_path / "original"
    link = tmp_path / "dados"
    original.mkdir()
    link.symlink_to(original, target_is_directory=True)
    store = Historico(link)
    record = store.save({"titulo": "Preservar"})
    moved = tmp_path / "organizado"
    original.rename(moved)
    link.unlink()
    link.symlink_to(moved, target_is_directory=True)
    assert store.save({"titulo": "Atualizado"}, record) == record
    assert json.loads(store.list()[0]["conteudo"])["titulo"] == "Atualizado"
    store.engine.dispose()


def test_real_readonly_error_is_not_retried(tmp_path, monkeypatch):
    import sqlite3

    from sqlalchemy.exc import OperationalError

    store = Historico(tmp_path)
    error = sqlite3.OperationalError("attempt to write a readonly database")
    error.sqlite_errorcode = sqlite3.SQLITE_READONLY
    calls = []

    def fail(*args):
        calls.append(args)
        raise OperationalError("INSERT", {}, error)

    monkeypatch.setattr(store, "_save", fail)
    with pytest.raises(OperationalError):
        store.save({"titulo": "Preservar"})
    assert len(calls) == 1 and store.list() == []
    store.engine.dispose()
