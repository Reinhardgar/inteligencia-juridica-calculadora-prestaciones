from pathlib import Path
import re, shutil, py_compile

ROOT = Path(__file__).resolve().parent
ui = ROOT / 'calculadora_prestaciones_ui_modern.py'
build = ROOT / 'Build-Calculadora.ps1'
logo = ROOT / 'logo_despacho.png'
icon = ROOT / 'calculadora_despacho_(1).ico'

for p in (ui, build, logo, icon):
    if not p.exists():
        raise SystemExit(f'Falta el archivo requerido: {p.name}')

shutil.copy2(ui, ui.with_suffix('.py.v1.2.bak'))
shutil.copy2(build, build.with_suffix('.ps1.v1.2.bak'))
text = ui.read_text(encoding='utf-8-sig')

if 'def resource_path(' not in text:
    text = text.replace('import json\n', 'import json\nimport os\nimport sys\n')
    marker = 'APP_VERSION = "1.0.0"\n'
    helper = '''APP_VERSION = "1.2.0"\n\ndef resource_path(nombre):\n    """Resuelve recursos tanto en desarrollo como dentro de PyInstaller."""\n    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))\n    return os.path.join(base, nombre)\n'''
    if marker not in text:
        raise SystemExit('No se encontró APP_VERSION en la interfaz.')
    text = text.replace(marker, helper)
else:
    text = re.sub(r'APP_VERSION\s*=\s*"[^"]+"', 'APP_VERSION = "1.2.0"', text, count=1)

if 'self.iconbitmap(resource_path("calculadora_despacho_(1).ico"))' not in text:
    needle = '        self.title(f"{APP_NAME} {APP_VERSION}")\n'
    repl = needle + '''        try:\n            self.iconbitmap(resource_path("calculadora_despacho_(1).ico"))\n        except Exception:\n            pass\n'''
    if needle not in text:
        raise SystemExit('No se encontró la inicialización de la ventana.')
    text = text.replace(needle, repl, 1)

if 'self.logo_header = tk.PhotoImage' not in text:
    needle = '        header.pack_propagate(False)\n'
    repl = needle + '''        self.logo_header = tk.PhotoImage(file=resource_path("logo_despacho.png"))\n        self.logo_header = self.logo_header.subsample(4, 4)\n        tk.Label(header, image=self.logo_header, bg="#102a43", bd=0).pack(\n            side="right", padx=24, pady=10\n        )\n'''
    if needle not in text:
        raise SystemExit('No se encontró el encabezado de la interfaz.')
    text = text.replace(needle, repl, 1)

clipboard_block = '''            # Copia automáticamente únicamente la cifra numérica total, sin $ ni separadores.\n            total_limpio = f"{r['total_prestaciones']:.2f}"\n            self.clipboard_clear()\n            self.clipboard_append(total_limpio)\n            self.update()\n'''
if 'total_limpio = f"{r[\'total_prestaciones\']:.2f}"' not in text:
    needle = '            self.total.configure(text=f"TOTAL: ${r[\'total_prestaciones\']:,.2f}")\n'
    if needle not in text:
        raise SystemExit('No se encontró la actualización del total.')
    text = text.replace(needle, needle + clipboard_block, 1)
    text = text.replace(
        'self.status.set(f"Calculo completado | {r[\'dias_relacion\']} dias | {r[\'anios_relacion\']:.4f} anos")',
        'self.status.set(f"Cálculo completado y total copiado | {r[\'dias_relacion\']} días | {r[\'anios_relacion\']:.4f} años")',
        1,
    )

ui.write_text(text, encoding='utf-8')
py_compile.compile(str(ui), doraise=True)

b = build.read_text(encoding='utf-8-sig')
if '--icon ".\\calculadora_despacho_(1).ico"' not in b:
    target = '  --name "CalculadoraPrestaciones" `\n'
    addition = '''  --icon ".\\calculadora_despacho_(1).ico" `\n  --add-data ".\\logo_despacho.png;." `\n  --add-data ".\\calculadora_despacho_(1).ico;." `\n'''
    if target not in b:
        raise SystemExit('No se encontró el comando PyInstaller esperado en Build-Calculadora.ps1.')
    b = b.replace(target, target + addition, 1)
build.write_text(b, encoding='utf-8-sig')

print('ACTUALIZACION_OK')
print('Interfaz: logotipo agregado')
print('Ejecutable: icono multirresolución configurado')
print('Portapapeles: total numérico sin formato al calcular')
print('Reconstruya con: .\\Build-Calculadora.ps1 -Clean')
