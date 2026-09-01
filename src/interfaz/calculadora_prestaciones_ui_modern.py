"""Interfaz moderna para la Calculadora de Prestaciones.
Conserva el motor de calculo de calculadora_prestaciones_consolidada.py.
"""
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from calculadora_prestaciones_consolidada import (
    Parametros, calcular_prestaciones, numero_seguro, parsear_fecha
)

APP_NAME = "Calculadora Juridico-Laboral"
APP_VERSION = "1.4.1"

def resource_path(nombre):
    """Resuelve recursos tanto en desarrollo como dentro de PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, nombre)

CONCEPTOS = [
    ("IC", "Indemnizacion constitucional"),
    ("IN", "20 días por año"),
    ("PA", "Prima de antiguedad"),
    ("VN", "Vacaciones"),
    ("PV", "Prima vacacional"),
    ("AN", "Aguinaldo"),
    ("PDN", "Prima dominical"),
    ("HX2N", "Horas extras"),
    ("DON", "Dias feriados"),
    ("D7N", "Septimos dias"),
    ("SF", "Semana de fondo"),
    ("FAC", "Fondo de ahorro"),
]

CAMPOS = [
    ("nombre", "Nombre del trabajador", ""),
    ("fecha_inicio", "Fecha de Ingreso", "dd-mm-aaaa"),
    ("fecha_salida", "Fecha de salida o corte", "dd-mm-aaaa"),
    ("salario_diario", "Salario diario (admite cálculos)", ""),
    ("salario_integrado", "Salario diario integrado (Opcional)", ""),
    ("cantidades_expresas", "Cantidades expresas (admite cálculos)", ""),
    ("fondo_ahorro", "Fondo de ahorro sin duplicar", "0.00"),
    ("salarios_devengados", "Dias de salario devengados", "0"),
]

class ModernApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        try:
            self.iconbitmap(resource_path("calculadora_despacho_(1).ico"))
        except Exception:
            pass
        self.geometry("1160x720")
        self.minsize(1020, 650)
        self.configure(bg="#f4f7fb")
        self.entries = {}
        self.vars = {k: tk.BooleanVar(value=False) for k, _ in CONCEPTOS}
        self.status = tk.StringVar(value="Listo")
        self._style()
        self._ui()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame", background="#f4f7fb")
        s.configure("Card.TFrame", background="#ffffff", relief="flat")
        s.configure("TLabel", background="#f4f7fb", foreground="#172033", font=("Segoe UI", 10))
        s.configure("Header.TLabel", background="#102a43", foreground="white", font=("Segoe UI Semibold", 20))
        s.configure("Sub.TLabel", background="#102a43", foreground="#d9e8f5", font=("Segoe UI", 10))
        s.configure("CardTitle.TLabel", background="#ffffff", foreground="#102a43", font=("Segoe UI Semibold", 12))
        s.configure("CardText.TLabel", background="#ffffff", foreground="#334e68", font=("Segoe UI", 10))
        s.configure("Accent.TButton", font=("Segoe UI Semibold", 10), padding=(16, 10), background="#1463ff", foreground="white")
        s.map("Accent.TButton", background=[("active", "#0d4fd1")])
        s.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        s.configure("Treeview", rowheight=30, font=("Segoe UI", 10), background="white", fieldbackground="white")
        s.configure("Treeview.Heading", font=("Segoe UI Semibold", 10), background="#eaf0f6")
        s.configure("TCheckbutton", background="#ffffff", font=("Segoe UI", 10))
        s.configure("TNotebook", background="#f4f7fb", borderwidth=0)
        s.configure("TNotebook.Tab", padding=(18, 9), font=("Segoe UI Semibold", 10))

    def _ui(self):
        header = tk.Frame(self, bg="#102a43", height=86)
        header.pack(fill="x")
        header.pack_propagate(False)
        self.logo_header = tk.PhotoImage(file=resource_path("logo_despacho.png"))
        self.logo_header = self.logo_header.subsample(4, 4)
        tk.Label(header, image=self.logo_header, bg="#102a43", bd=0).pack(
            side="right", padx=24, pady=10
        )
        ttk.Label(header, text=APP_NAME, style="Header.TLabel").pack(anchor="w", padx=28, pady=(15, 0))
        ttk.Label(header, text="Calculo trazable, exportable y preparado para revision juridica", style="Sub.TLabel").pack(anchor="w", padx=29)

        body = ttk.Frame(self, padding=18)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=5)
        body.columnconfigure(1, weight=4)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body, style="Card.TFrame", padding=18)
        right = ttk.Frame(body, style="Card.TFrame", padding=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        right.grid(row=0, column=1, sticky="nsew", padx=(9, 0))
        left.columnconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        ttk.Label(left, text="Datos del expediente", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        for i, (key, label, hint) in enumerate(CAMPOS, start=1):
            ttk.Label(left, text=label, style="CardText.TLabel").grid(row=i, column=0, sticky="w", pady=6, padx=(0, 12))
            e = ttk.Entry(left)
            e.grid(row=i, column=1, sticky="ew", pady=6)
            self.entries[key] = e
            if hint and hint not in ("Opcional", "dd-mm-aaaa"):
                e.insert(0, hint)

        params = ttk.LabelFrame(left, text="Parametros juridicos y de calculo", padding=12)
        params.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(14, 8))
        self.dias_ind = tk.StringVar(value="90")
        self.dias_vac = tk.StringVar(value="")
        self.prima_vac = tk.StringVar(value="0.25")
        self.dias_ag = tk.StringVar(value="15")
        self.horas_ex = tk.StringVar(value="9")
        pdefs = [("Dias indemnizacion", self.dias_ind), ("Días de vacaciones", self.dias_vac),
                 ("Prima vacacional", self.prima_vac), ("Dias aguinaldo", self.dias_ag),
                 ("Horas extra/semana", self.horas_ex)]
        for i, (txt, var) in enumerate(pdefs):
            ttk.Label(params, text=txt).grid(row=i//2, column=(i%2)*2, sticky="w", padx=(0, 6), pady=4)
            ttk.Entry(params, textvariable=var, width=12).grid(row=i//2, column=(i%2)*2+1, sticky="w", padx=(0, 16), pady=4)

        actions = ttk.Frame(left, style="Card.TFrame")
        actions.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(actions, text="Calcular", style="Accent.TButton", command=self.calcular).pack(side="left")
        ttk.Button(actions, text="Limpiar", command=self.limpiar).pack(side="left", padx=8)
        ttk.Button(actions, text="Importar Excel", command=self.importar_excel).pack(side="left")

        ttk.Label(right, text="Prestaciones a incluir", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        checks = ttk.Frame(right, style="Card.TFrame")
        checks.grid(row=1, column=0, sticky="ew", pady=(10, 14))
        for i, (key, label) in enumerate(CONCEPTOS):
            ttk.Checkbutton(checks, text=label, variable=self.vars[key]).grid(row=i//2, column=i%2, sticky="w", padx=(0, 18), pady=4)

        result = ttk.Frame(right, style="Card.TFrame")
        result.grid(row=2, column=0, sticky="nsew")
        result.rowconfigure(0, weight=1)
        result.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(result, columns=("concepto", "importe"), show="headings")
        self.tree.heading("concepto", text="Concepto")
        self.tree.heading("importe", text="Importe")
        self.tree.column("concepto", width=240)
        self.tree.column("importe", width=140, anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(result, orient="vertical", command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)

        self.total = ttk.Label(right, text="TOTAL: $0.00", style="CardTitle.TLabel")
        self.total.grid(row=3, column=0, sticky="e", pady=(14, 8))
        out = ttk.Frame(right, style="Card.TFrame")
        out.grid(row=4, column=0, sticky="ew")
        ttk.Button(out, text="Copiar resumen", command=self.copiar).pack(side="right")
        ttk.Button(out, text="Guardar JSON", command=self.guardar_json).pack(side="right", padx=8)

        bar = ttk.Label(self, textvariable=self.status, anchor="w", padding=(12, 6))
        bar.pack(fill="x")
        self.ultimo_resultado = None

    def _params(self):
        sd = numero_seguro(self.entries["salario_diario"].get())
        sdi = numero_seguro(self.entries["salario_integrado"].get(), sd)
        return Parametros(
            nombre=self.entries["nombre"].get().strip(),
            fecha_inicio=parsear_fecha(self.entries["fecha_inicio"].get()),
            fecha_salida=parsear_fecha(self.entries["fecha_salida"].get()),
            salario_diario=sd,
            salario_diario_integrado=sdi,
            cantidades_expresas=numero_seguro(self.entries["cantidades_expresas"].get()),
            fondo_ahorro=numero_seguro(self.entries["fondo_ahorro"].get()),
            dias_salario_devengado=numero_seguro(self.entries["salarios_devengados"].get()),
            dias_indemnizacion=numero_seguro(self.dias_ind.get(), 90),
            dias_vacaciones_manual=numero_seguro(self.dias_vac.get()),
            prima_vacacional=numero_seguro(self.prima_vac.get(), .25),
            dias_aguinaldo=numero_seguro(self.dias_ag.get(), 15),
            horas_extra_semanales=numero_seguro(self.horas_ex.get(), 9),
        )

    def calcular(self):
        try:
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
            self.total.configure(text=f"TOTAL: ${r['total_prestaciones']:,.2f}")
            # Copia automáticamente únicamente la cifra numérica total, sin $ ni separadores.
            total_limpio = f"{r['total_prestaciones']:.2f}"
            self.clipboard_clear()
            self.clipboard_append(total_limpio)
            self.update()
            self.status.set(f"Cálculo completado y total copiado | {r['dias_relacion']} días | {r['anios_relacion']:.4f} años")
        except Exception as exc:
            messagebox.showerror("Revise los datos", str(exc))
            self.status.set("No se pudo completar el calculo")

    def copiar(self):
        if not self.ultimo_resultado: return
        lines = [f"Trabajador: {self.ultimo_resultado['Nm']}"]
        for item in self.tree.get_children():
            c, v = self.tree.item(item, "values"); lines.append(f"{c}: {v}")
        lines.append(self.total.cget("text"))
        self.clipboard_clear(); self.clipboard_append("\n".join(lines))
        self.status.set("Resumen copiado")

    def guardar_json(self):
        if not self.ultimo_resultado: return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f: json.dump(self.ultimo_resultado, f, ensure_ascii=False, indent=2)
            self.status.set("JSON guardado")

    def limpiar(self):
        for e in self.entries.values(): e.delete(0, "end")
        for v in self.vars.values(): v.set(False)
        for item in self.tree.get_children(): self.tree.delete(item)
        self.total.configure(text="TOTAL: $0.00")
        self.ultimo_resultado = None; self.status.set("Formulario limpio")

    def importar_excel(self):
        messagebox.showinfo("Importacion", "La importacion masiva permanece disponible en la version consolidada. Para produccion conviene agregar una vista de validacion previa por filas.")

if __name__ == "__main__":
    ModernApp().mainloop()

