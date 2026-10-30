# Build local: .venv/bin/pyinstaller --noconfirm --distpath /private/tmp/planejador-build packaging/Planejador.spec
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
          upx=False, console=False, argv_emulation=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=name)
app = BUNDLE(coll, name=name + '.app',
             icon=str(root / 'frontend/assets/app.icns'),
             bundle_identifier='br.lucasmontalvao.planejador',
             info_plist={'CFBundleDisplayName': name,
                         'CFBundleName': name,
                         'CFBundleShortVersionString': '0.1.0',
                         'NSHighResolutionCapable': True})

# Finder/resource-fork metadata can prevent signing copied build resources.
# This cleanup is restricted to the newly generated app, never user files.
import subprocess
bundle_path = str(Path(DISTPATH) / (name + '.app'))
subprocess.run(['xattr', '-cr', bundle_path], check=True)
subprocess.run(['codesign', '--force', '--deep', '--sign', '-', '--timestamp=none', bundle_path], check=True)
subprocess.run(['codesign', '--verify', '--deep', '--strict', bundle_path], check=True)
