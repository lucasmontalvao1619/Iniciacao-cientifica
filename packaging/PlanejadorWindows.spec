# Executar somente no Windows: ver build-windows.ps1
from pathlib import Path

root = Path(SPECPATH).parent
name = 'Planejador de Experimentos'
a = Analysis(
    [str(root / 'packaging/macos_entry.py')],
    pathex=[str(root), str(root / 'backend')],
    binaries=[],
    datas=[(str(root / 'frontend/protocolos.json'), 'frontend'),
           (str(root / 'frontend/assets'), 'frontend/assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={'matplotlib': {'backends': ['QtAgg']}},
    excludes=['tkinter', 'PySide6', 'PySide2', 'PyQt5', 'pytest', 'IPython'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=name,
          debug=False, bootloader_ignore_signals=False, strip=False,
          upx=False, console=False, icon=str(root / "frontend/assets/app.png"))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=name)

# A pasta acompanha o executável portátil e recebe os registros arquivados.
archive = Path(DISTPATH) / name / 'Registros de Experimentos'
archive.mkdir(exist_ok=True)
(archive / 'LEIA-ME.txt').write_text(
    'Registros arquivados são JSON para consulta e exportação. Não são sessões reabertas. '
    'Se esta pasta não permitir gravação, o aplicativo usa a pasta de dados do usuário e mostra o caminho na tela inicial.',
    encoding='utf-8',
)
