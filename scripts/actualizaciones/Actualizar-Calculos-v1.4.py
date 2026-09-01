from pathlib import Path
import shutil
import py_compile

ROOT = Path(__file__).resolve().parent
MOTOR = ROOT / "calculadora_prestaciones_consolidada.py"
if not MOTOR.exists():
    raise SystemExit(f"No se encontró {MOTOR.name} en {ROOT}")

BACKUP = MOTOR.with_name(MOTOR.name + ".v1.4.bak")
shutil.copy2(MOTOR, BACKUP)
text = MOTOR.read_text(encoding="utf-8-sig")

cambios = {
'''    fraccion_ultimo_anio = max(0.0, (fs - ultimo_aniversario).days / 365.0)
''': '''    dias_ultimo_periodo = (fs - ultimo_aniversario).days
    # Si el corte coincide exactamente con un aniversario, el último periodo
    # anual se considera completado al 100%, no en cero.
    fraccion_ultimo_anio = (
        1.0 if total_dias > 0 and dias_ultimo_periodo == 0
        else max(0.0, min(dias_ultimo_periodo / 365.0, 1.0))
    )
''',
'''    prima_dominical = p.salario_diario * 0.25 * 52 * min(anios_totales, 1)
    horas_extra = (
        p.horas_extra_semanales * 2 * p.salario_diario * 52 / 8
        * min(anios_totales, 1)
    )
''': '''    # Prima dominical proporcional a semanas trabajadas, con máximo de 52.
    semanas_calculo = min(total_dias / 7.0, 52.0)
    prima_dominical = p.salario_diario * 0.25 * semanas_calculo

    # Hasta 9 horas semanales se pagan al doble; el excedente, al triple.
    horas_dobles = min(p.horas_extra_semanales, 9.0)
    horas_triples = max(p.horas_extra_semanales - 9.0, 0.0)
    horas_extra = (
        ((horas_dobles * 2.0) + (horas_triples * 3.0))
        * (p.salario_diario / 8.0)
        * semanas_calculo
    )
'''
}

for viejo, nuevo in cambios.items():
    if viejo not in text:
        shutil.copy2(BACKUP, MOTOR)
        raise SystemExit("No se encontró un bloque esperado. No se aplicaron cambios.")
    text = text.replace(viejo, nuevo, 1)

MOTOR.write_text(text, encoding="utf-8")
try:
    py_compile.compile(str(MOTOR), doraise=True)
except Exception:
    shutil.copy2(BACKUP, MOTOR)
    raise

print("ACTUALIZACION_OK")
print("- Prima dominical: semanas proporcionales, máximo 52")
print("- Horas extra: hasta 9 dobles y excedente triples")
print("- Vacaciones: aniversario exacto equivale a 100% del último periodo")
print(f"Respaldo: {BACKUP.name}")
print("Reconstruya con: .\\Build-Calculadora.ps1 -Clean")
