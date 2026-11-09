import pytest

from planejador.services.arquivos import gravacao_atomica


def test_failed_export_preserves_existing_file_and_removes_temporary(tmp_path):
    path = tmp_path / "coleta.xlsx"
    path.write_bytes(b"original")
    with pytest.raises(OSError), gravacao_atomica(path) as temporary:
        temporary.write_bytes(b"incompleto")
        raise OSError("disco cheio")
    assert path.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [path]
    with gravacao_atomica(path) as temporary:
        temporary.write_bytes(b"completo")
    assert path.read_bytes() == b"completo"
