from pathlib import Path
import shutil, py_compile

root = Path(__file__).resolve().parent
motor = root / "calculadora_prestaciones_consolidada.py"
if not motor.exists():
    raise SystemExit(f"No se encontró {motor.name}")
backup = motor.with_name(motor.name + ".v1.4.1.bak")
shutil.copy2(motor, backup)
text = motor.read_text(encoding="utf-8-sig")
old = '''    anios_cumplidos = max(0, int((ultimo_aniversario - fi).days / 365))
    sistema_vacaciones = VACACIONES_NUEVO if fs.year > 2022 else VACACIONES_ANTERIOR
    indice = min(anios_cumplidos, len(sistema_vacaciones) - 1)
'''
new = '''    anios_cumplidos = max(0, int((ultimo_aniversario - fi).days / 365))
    sistema_vacaciones = VACACIONES_NUEVO if fs.year > 2022 else VACACIONES_ANTERIOR
    # Durante un periodo en curso se usa el nivel del año que se está trabajando.
    # En aniversario exacto se liquida al 100% el periodo que acaba de concluir.
    anio_vacacional = (
        max(anios_cumplidos - 1, 0)
        if total_dias > 0 and dias_ultimo_periodo == 0
        else anios_cumplidos
    )
    indice = min(anio_vacacional, len(sistema_vacaciones) - 1)
'''
if old not in text:
    raise SystemExit("No se encontró el bloque esperado; no se modificó el motor.")
text = text.replace(old, new, 1)
motor.write_text(text, encoding="utf-8")
try:
    py_compile.compile(str(motor), doraise=True)
except Exception:
    shutil.copy2(backup, motor)
    raise
print("CORRECCION_OK")
print("Aniversario exacto: liquida al 100% el periodo recién concluido.")
print("Ejemplo primer aniversario 2026: 12 días, no 14.")
