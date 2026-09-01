param(
    [switch]$RebuildApp
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($RebuildApp) {
    Stop-Process -Name "CalculadoraPrestaciones" -Force -ErrorAction SilentlyContinue
    & "$PSScriptRoot\Build-Calculadora.ps1" -Clean
    if ($LASTEXITCODE -ne 0) { throw "Falló la compilación de la aplicación." }
}

$Exe = Join-Path $PSScriptRoot "dist\CalculadoraPrestaciones\CalculadoraPrestaciones.exe"
if (-not (Test-Path $Exe)) {
    throw "No se encontró $Exe. Compile primero la aplicación."
}

$Candidates = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 7\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 7\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 7\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
)
$ISCC = $Candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $ISCC) {
    throw "No se encontró ISCC.exe. Instale Inno Setup y vuelva a ejecutar este script."
}

& $ISCC "$PSScriptRoot\CalculadoraPrestaciones.iss"
if ($LASTEXITCODE -ne 0) { throw "Falló la creación del instalador." }

$Installer = Get-ChildItem "$PSScriptRoot\Instalador\Instalador_CalculadoraPrestaciones_v*.exe" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $Installer) { throw "La compilación terminó, pero no se localizó el instalador." }

Write-Host "Instalador creado correctamente:" -ForegroundColor Green
Write-Host $Installer.FullName
