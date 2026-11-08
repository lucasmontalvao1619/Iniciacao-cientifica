"""Monta a distribuição com POPs e registros após a compilação nativa."""

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from frontend.pop import write_pop_docx  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--platform", choices=["mac", "windows"], required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
name = "Planejador de Experimentos"
output = root / "dist"
source = (
    Path("/private/tmp/planejador-build") / (name + ".app")
    if args.platform == "mac"
    else output / "windows" / name
)
stage = output / "release" / name
stage.mkdir(parents=True, exist_ok=True)
if args.platform == "mac":
    subprocess.run(
        ["ditto", "--norsrc", "--noextattr", str(source), str(stage / source.name)],
        check=True,
    )
else:
    shutil.copytree(source, stage, dirs_exist_ok=True)
pops = stage / "POPs"
pops.mkdir(exist_ok=True)
for protocol in json.loads(
    (root / "frontend/protocolos.json").read_text(encoding="utf-8")
):
    write_pop_docx(protocol, pops / (protocol["id"] + ".docx"))
archive = stage / "Registros de Experimentos"
archive.mkdir(exist_ok=True)
(archive / "LEIA-ME.txt").write_text(
    "Registros arquivados para consulta/exportação. O aplicativo informa o caminho efetivo; os dados do usuário não são apagados na atualização.",
    encoding="utf-8",
)
(stage / "LEIA-ME.txt").write_text(
    "Planejador de Experimentos 0.2.0\nDez protocolos PREP com planejamento, POPs, medições, estatística e gráficos. Fontes e limites constam nos POPs. Valores planejados não substituem medições ou conferência do método.\n",
    encoding="utf-8",
)
if args.platform == "mac":
    subprocess.run(["xattr", "-cr", str(stage)], check=True)
    subprocess.run(
        ["codesign", "--verify", "--deep", "--strict", str(stage / source.name)],
        check=True,
    )
    target = output / "Planejador-Mac.zip"
    subprocess.run(
        [
            "ditto",
            "--norsrc",
            "--noextattr",
            "-c",
            "-k",
            "--keepParent",
            str(stage),
            str(target),
        ],
        check=True,
    )
else:
    target = Path(
        shutil.make_archive(
            str(output / "Planejador-Windows-Portatil"),
            "zip",
            root_dir=stage.parent,
            base_dir=name,
        )
    )
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    assert (
        len([n for n in z.namelist() if "/POPs/PREP-" in n and n.endswith(".docx")])
        == 10
    )
print(target)
