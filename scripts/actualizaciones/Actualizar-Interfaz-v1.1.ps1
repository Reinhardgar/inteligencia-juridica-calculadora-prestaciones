$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$Path = Join-Path $PSScriptRoot "calculadora_prestaciones_ui_modern.py"
if (-not (Test-Path $Path)) {
    throw "No se encontró calculadora_prestaciones_ui_modern.py en $PSScriptRoot"
}

$Backup = "$Path.bak"
Copy-Item $Path $Backup -Force
$Text = Get-Content $Path -Raw -Encoding UTF8

$Text = $Text.Replace(
    '("salario_integrado", "Salario diario integrado", "Opcional")',
    '("salario_integrado", "Salario diario integrado (Opcional)", "")'
)
$Text = $Text.Replace(
    '("salario_diario", "Salario diario", "0.00")',
    '("salario_diario", "Salario diario (admite cálculos)", "")'
)
$Text = $Text.Replace(
    '("cantidades_expresas", "Cantidades expresas", "0.00")',
    '("cantidades_expresas", "Cantidades expresas (admite cálculos)", "")'
)
$Text = $Text.Replace(
    '("Vacaciones manuales", self.dias_vac)',
    '("Días de vacaciones", self.dias_vac)'
)
$Text = $Text.Replace(
    '    ("FAC", "Fondo de ahorro"),`r`n',
    ''
)
$Text = $Text.Replace(
    '    ("FAC", "Fondo de ahorro"),`n',
    ''
)

$Old = @'
            p = self._params()
            sel = {k: v.get() for k, v in self.vars.items()}
            if not any(sel.values()):
                raise ValueError("Seleccione al menos una prestacion.")
            r = calcular_prestaciones(p, sel)
            self.ultimo_resultado = r
            for item in self.tree.get_children(): self.tree.delete(item)
            labels = dict(CONCEPTOS)
            for key, _ in CONCEPTOS:
                if sel[key]: self.tree.insert("", "end", values=(labels[key], f"${r[key]:,.2f}"))
'@

$New = @'
            p = self._params()
            sel = {k: v.get() for k, v in self.vars.items()}
            # El fondo de ahorro se cuantifica automáticamente al capturar una cantidad.
            sel["FAC"] = p.fondo_ahorro > 0
            if not any(sel.values()):
                raise ValueError("Seleccione al menos una prestación o capture fondo de ahorro.")
            r = calcular_prestaciones(p, sel)
            self.ultimo_resultado = r
            for item in self.tree.get_children(): self.tree.delete(item)
            labels = dict(CONCEPTOS)
            labels["FAC"] = "Fondo de ahorro"
            orden_salida = [k for k, _ in CONCEPTOS] + ["FAC"]
            for key in orden_salida:
                if sel.get(key, False):
                    self.tree.insert("", "end", values=(labels[key], f"${r[key]:,.2f}"))
'@

if (-not $Text.Contains($Old)) {
    throw "No se encontró el bloque esperado de cálculo. Se restaurará el archivo original."
}
$Text = $Text.Replace($Old, $New)

Set-Content $Path $Text -Encoding UTF8

& .\.venv\Scripts\python.exe -m py_compile $Path
if ($LASTEXITCODE -ne 0) {
    Copy-Item $Backup $Path -Force
    throw "La validación de sintaxis falló. Se restauró el respaldo."
}

Write-Host "Interfaz actualizada correctamente." -ForegroundColor Green
Write-Host "Respaldo: $Backup"
Write-Host "Ahora reconstruya con: .\Build-Calculadora.ps1 -Clean"
