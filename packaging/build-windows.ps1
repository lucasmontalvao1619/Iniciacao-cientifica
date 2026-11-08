# Execute no PowerShell do Windows com Python 3.11 ou superior instalado.
$ErrorActionPreference = "Stop"
if ($env:OS -ne "Windows_NT") { throw "Este script precisa ser executado no Windows." }
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Não foi possível criar o ambiente Python." }
}
& .venv\Scripts\python.exe -m pip install -e ".[ui,bundle]"
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar as dependências." }
& .venv\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist/windows packaging/PlanejadorWindows.spec
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar o executável Windows." }
# Gerar os POPs pela mesma função usada no aplicativo, com as imagens e créditos atuais.
$popScript = @'
import json
from pathlib import Path
from frontend.pop import write_pop_docx
output = Path("dist/windows/Planejador de Experimentos/POPs")
output.mkdir(exist_ok=True)
for protocol in json.loads(Path("frontend/protocolos.json").read_text(encoding="utf-8")):
    if protocol.get("tipo_calculo"):
        write_pop_docx(protocol, output / (protocol["id"] + ".docx"))
'@
$popScript | & .venv\Scripts\python.exe -
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar os POPs para o pacote Windows." }
Compress-Archive -Path "dist/windows/Planejador de Experimentos" -DestinationPath "dist/Planejador-Windows.zip" -Force
Write-Output "Gerado: dist/Planejador-Windows.zip. Extrair antes de executar e validar neste Windows."
