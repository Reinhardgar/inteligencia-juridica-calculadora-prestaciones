from pathlib import Path
import shutil
import py_compile

root = Path(__file__).resolve().parent
ui = root / "calculadora_prestaciones_ui_modern.py"

if not ui.exists():
    raise SystemExit(f"No se encontró {ui.name} en {root}")

backup = ui.with_name(ui.name + ".v1.3.bak")
shutil.copy2(ui, backup)
text = ui.read_text(encoding="utf-8-sig")

reemplazos = {
    '"20 dias por ano"': '"20 días por año"',
    '"20 dias por anio"': '"20 días por año"',
    '"20 días por ano"': '"20 días por año"',
    '"Fecha de inicio"': '"Fecha de Ingreso"',
    '"Fecha de inicio (dd-mm-yyyy):"': '"Fecha de Ingreso (dd-mm-yyyy):"',
}

cambios = 0
for anterior, nuevo in reemplazos.items():
    if anterior in text:
        text = text.replace(anterior, nuevo)
        cambios += 1

if cambios == 0:
    raise SystemExit("No se localizaron los textos esperados. No se modificó el archivo.")

ui.write_text(text, encoding="utf-8")
try:
    py_compile.compile(str(ui), doraise=True)
except Exception:
    shutil.copy2(backup, ui)
    raise

print("ACTUALIZACION_OK")
print(f"Reemplazos aplicados: {cambios}")
print(f"Respaldo: {backup.name}")
print("Reconstruya con: .\\Build-Calculadora.ps1 -Clean")
