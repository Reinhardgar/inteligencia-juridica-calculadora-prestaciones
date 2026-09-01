param([switch]$Clean)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if ($Clean) { Remove-Item -Recurse -Force build,dist -ErrorAction SilentlyContinue }
if (-not (Test-Path .venv)) { py -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\pyinstaller.exe --noconfirm --clean --onedir --windowed `
  --name "CalculadoraPrestaciones" `
  --icon ".\calculadora_despacho_(1).ico" `
  --add-data ".\logo_despacho.png;." `
  --add-data ".\calculadora_despacho_(1).ico;." `
  calculadora_prestaciones_ui_modern.py
Write-Host "Ejecutable creado en dist\CalculadoraPrestaciones\CalculadoraPrestaciones.exe" -ForegroundColor Green
