[CmdletBinding()]
param(
    [string]$Origen = "C:\Users\HP980\Downloads\CalculadoraDespacho",
    [string]$DestinoRaiz = "C:\Users\HP980\Documents\InteligenciaJuridica",
    [string]$NombreRepositorio = "inteligencia-juridica-calculadora-prestaciones",
    [string]$Version = "1.4.1",
    [ValidateSet("private", "internal", "public")]
    [string]$Visibilidad = "private"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Require-Command {
    param([string]$Name, [string]$InstallCommand)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "No se encontró '$Name'. Instálelo con: $InstallCommand"
    }
}

function Copy-IfExists {
    param([string]$Source, [string]$Destination)
    if (Test-Path -LiteralPath $Source) {
        $parent = Split-Path -Parent $Destination
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        Write-Host "Copiado: $Source" -ForegroundColor DarkGray
    }
}

Require-Command git "winget install --id Git.Git --exact"
Require-Command gh  "winget install --id GitHub.cli --exact"

if (-not (Test-Path -LiteralPath $Origen)) {
    throw "La carpeta de origen no existe: $Origen"
}

# Autenticación segura mediante navegador. No guarda tokens en el script.
& gh auth status *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Se abrirá el inicio de sesión seguro de GitHub..." -ForegroundColor Cyan
    & gh auth login --hostname github.com --git-protocol https --web
    if ($LASTEXITCODE -ne 0) { throw "No se completó la autenticación con GitHub." }
}

$Repo = Join-Path $DestinoRaiz $NombreRepositorio
if (Test-Path -LiteralPath $Repo) {
    throw "El destino ya existe: $Repo. Renómbrelo, elimínelo o use otro NombreRepositorio."
}

$Dirs = @(
    "src\motor", "src\interfaz", "src\configuracion",
    "tests", "assets", "packaging\pyinstaller", "packaging\inno-setup",
    "scripts\actualizaciones", "docs\arquitectura", "docs\juridico",
    "releases\v$Version"
)
New-Item -ItemType Directory -Path $Repo -Force | Out-Null
foreach ($d in $Dirs) { New-Item -ItemType Directory -Path (Join-Path $Repo $d) -Force | Out-Null }

# Código fuente vigente.
Copy-IfExists (Join-Path $Origen "calculadora_prestaciones_consolidada.py") (Join-Path $Repo "src\motor\calculadora_prestaciones_consolidada.py")
Copy-IfExists (Join-Path $Origen "calculadora_prestaciones_ui_modern.py") (Join-Path $Repo "src\interfaz\calculadora_prestaciones_ui_modern.py")

# Pruebas, recursos, empaquetado y scripts de actualización.
Get-ChildItem -LiteralPath $Origen -Filter "Pruebas-*.py" -File -ErrorAction SilentlyContinue |
    ForEach-Object { Copy-Item $_.FullName (Join-Path $Repo "tests\$($_.Name)") -Force }
Get-ChildItem -LiteralPath $Origen -Include "*.png","*.ico" -File -ErrorAction SilentlyContinue |
    ForEach-Object { Copy-Item $_.FullName (Join-Path $Repo "assets\$($_.Name)") -Force }
Copy-IfExists (Join-Path $Origen "Build-Calculadora.ps1") (Join-Path $Repo "packaging\pyinstaller\Build-Calculadora.ps1")
Copy-IfExists (Join-Path $Origen "CalculadoraPrestaciones.spec") (Join-Path $Repo "packaging\pyinstaller\CalculadoraPrestaciones.spec")
Copy-IfExists (Join-Path $Origen "Build-Installer.ps1") (Join-Path $Repo "packaging\inno-setup\Build-Installer.ps1")
Copy-IfExists (Join-Path $Origen "CalculadoraPrestaciones.iss") (Join-Path $Repo "packaging\inno-setup\CalculadoraPrestaciones.iss")
Copy-IfExists (Join-Path $Origen "requirements.txt") (Join-Path $Repo "requirements.txt")
Get-ChildItem -LiteralPath $Origen -Include "Actualizar-*.py","Actualizar-*.ps1","Corregir-*.py" -File -ErrorAction SilentlyContinue |
    ForEach-Object { Copy-Item $_.FullName (Join-Path $Repo "scripts\actualizaciones\$($_.Name)") -Force }

# Conserva el instalador publicado como activo de la versión, si existe.
$Installer = Get-ChildItem -Path (Join-Path $Origen "Instalador") -Filter "Instalador_CalculadoraPrestaciones_v$Version.exe" -File -ErrorAction SilentlyContinue | Select-Object -First 1
if ($Installer) {
    Copy-Item $Installer.FullName (Join-Path $Repo "releases\v$Version\$($Installer.Name)") -Force
}

@"
# Calculadora Jurídico-Laboral

Módulo de **Inteligencia Jurídica** para cuantificar prestaciones laborales y apoyar la estimación del monto reclamado al presentar una demanda.

## Versión estable

$Version

## Estructura

- `src/motor`: reglas y operaciones de cálculo.
- `src/interfaz`: aplicación de escritorio.
- `tests`: pruebas automatizadas.
- `assets`: logotipo e iconos.
- `packaging`: compilación PyInstaller e instalador Inno Setup.
- `scripts/actualizaciones`: migraciones históricas del código.
- `docs`: decisiones técnicas y jurídicas.
- `releases`: instaladores aprobados por versión.

## Validación

Los resultados son auxiliares y deben revisarse conforme a los hechos, documentos y criterio jurídico aplicable a cada expediente.

## Seguridad

No almacenar contraseñas, tokens, expedientes, datos personales ni bases productivas en este repositorio.
"@ | Set-Content -LiteralPath (Join-Path $Repo "README.md") -Encoding UTF8

@"
# Historial de cambios

## [$Version]

- Motor con prima dominical proporcional hasta 52 semanas.
- Horas extras: hasta 9 dobles y excedente manual al triple.
- Vacaciones proporcionales del último periodo y corrección de aniversario exacto.
- Interfaz moderna, portapapeles e instalador de Windows.
"@ | Set-Content -LiteralPath (Join-Path $Repo "CHANGELOG.md") -Encoding UTF8

@"
# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Empaquetado temporal
build/
dist/
*.spec.bak

# IDE y sistema
.vscode/
.idea/
.DS_Store
Thumbs.db

# Respaldos y temporales
*.bak
*.tmp
*.log

# Datos y secretos
.env
.env.*
*.pfx
*.pem
*.key
*.csv
*.xlsx
*.xls
*.json
!tests/fixtures/*.json

# Expedientes y documentos jurídicos
*.pdf
*.doc
*.docx
"@ | Set-Content -LiteralPath (Join-Path $Repo ".gitignore") -Encoding UTF8

@"
# Política de seguridad

Reporte cualquier vulnerabilidad directamente al responsable técnico del proyecto. No publique credenciales, archivos de expedientes ni datos personales en incidencias, commits o solicitudes de cambio.
"@ | Set-Content -LiteralPath (Join-Path $Repo "SECURITY.md") -Encoding UTF8

@"
# Decisiones de arquitectura

1. El motor de cálculo permanece separado de la interfaz.
2. Las reglas legales parametrizables deberán salir progresivamente del código hacia configuración versionada.
3. Dataverse será la fuente operativa futura; la calculadora no almacenará credenciales ni acceso directo incrustado.
4. Cada versión estable debe incluir pruebas, changelog e instalador trazable.
"@ | Set-Content -LiteralPath (Join-Path $Repo "docs\arquitectura\DECISIONES.md") -Encoding UTF8

Push-Location $Repo
try {
    & git init -b main
    & git config user.name "Reinhard Rafael García López"
    $email = (& gh api user --jq .email 2>$null)
    if ([string]::IsNullOrWhiteSpace($email)) { $email = "ReinhardGarciaLopez@AMDTPS.onmicrosoft.com" }
    & git config user.email $email
    & git add .
    & git commit -m "chore: estructura inicial y versión $Version"
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el commit inicial." }

    $Description = "Módulo de Inteligencia Jurídica para cálculo de prestaciones laborales"
    & gh repo create $NombreRepositorio --$Visibilidad --source . --remote origin --push --description $Description
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear o publicar el repositorio en GitHub." }

    & git tag -a "v$Version" -m "Versión estable $Version"
    & git push origin "v$Version"
    if ($LASTEXITCODE -ne 0) { throw "El repositorio se creó, pero no se pudo publicar la etiqueta v$Version." }

    if ($Installer) {
        & gh release create "v$Version" "releases\v$Version\$($Installer.Name)" --title "Calculadora Jurídico-Laboral v$Version" --notes "Versión estable para uso interno. Resultado sujeto a validación jurídica."
        if ($LASTEXITCODE -ne 0) { Write-Warning "El repositorio y la etiqueta se crearon, pero fue necesario revisar la publicación del instalador." }
    }

    Write-Host "Repositorio creado y publicado correctamente." -ForegroundColor Green
    & gh repo view --web
}
finally {
    Pop-Location
}
