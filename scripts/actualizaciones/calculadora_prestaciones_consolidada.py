import ast
import operator
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

try:
    import pandas as pd
except ImportError:
    pd = None

TOPES_DOBLE_SALARIO_MINIMO = {
    2017: 168.94,
    2018: 176.72,
    2019: 205.36,
    2020: 246.44,
    2021: 283.40,
    2022: 345.74,
    2023: 414.88,
    2024: 496.00,
    2025: 557.60,
    2026: 630.08,
}

VACACIONES_NUEVO = [12, 14, 16, 18, 20, 22, 22, 22, 22, 22,
                     24, 24, 24, 24, 24, 26, 26, 26, 26, 26,
                     28, 28, 28, 28, 28, 30, 30, 30, 30, 30,
                     32, 32, 32, 32, 32]
VACACIONES_ANTERIOR = [6, 8, 10, 12, 14, 14, 14, 14, 14, 16,
                       16, 16, 16, 16, 18, 18, 18, 18, 18, 20,
                       20, 20, 20, 20, 22, 22, 22, 22, 22, 24,
                       24, 24, 24, 24]

_OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def numero_seguro(texto, predeterminado=0.0):
    """Acepta números o cálculos aritméticos simples, sin usar eval()."""
    if texto is None or str(texto).strip() == "":
        return float(predeterminado)

    nodo = ast.parse(str(texto).replace(",", ""), mode="eval")

    def evaluar(n):
        if isinstance(n, ast.Expression):
            return evaluar(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.BinOp) and type(n.op) in _OPERADORES:
            return _OPERADORES[type(n.op)](evaluar(n.left), evaluar(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPERADORES:
            return _OPERADORES[type(n.op)](evaluar(n.operand))
        raise ValueError("Solo se permiten números y operaciones +, -, * y /.")

    valor = float(evaluar(nodo))
    if valor < 0:
        raise ValueError("Los importes y días no pueden ser negativos.")
    return valor


def parsear_fecha(texto):
    return datetime.strptime(str(texto).strip(), "%d-%m-%Y")


def aniversario_anterior(fecha_inicio, fecha_corte):
    try:
        aniversario = fecha_inicio.replace(year=fecha_corte.year)
    except ValueError:
        aniversario = fecha_inicio.replace(year=fecha_corte.year, day=28)
    if aniversario > fecha_corte:
        try:
            aniversario = fecha_inicio.replace(year=fecha_corte.year - 1)
        except ValueError:
            aniversario = fecha_inicio.replace(year=fecha_corte.year - 1, day=28)
    return aniversario


def tope_antiguedad(anio):
    if anio not in TOPES_DOBLE_SALARIO_MINIMO:
        raise ValueError(
            f"No existe tope de prima de antigüedad configurado para {anio}."
        )
    return TOPES_DOBLE_SALARIO_MINIMO[anio]


@dataclass
class Parametros:
    nombre: str
    fecha_inicio: datetime
    fecha_salida: datetime
    salario_diario: float
    salario_diario_integrado: float
    cantidades_expresas: float = 0.0
    fondo_ahorro: float = 0.0
    dias_salario_devengado: float = 0.0
    dias_indemnizacion: float = 90.0
    dias_vacaciones_manual: float = 0.0
    prima_vacacional: float = 0.25
    dias_aguinaldo: float = 15.0
    horas_extra_semanales: float = 9.0


def calcular_prestaciones(p, seleccion):
    fi, fs = p.fecha_inicio, p.fecha_salida
    if fs < fi:
        raise ValueError("La fecha de salida no puede ser anterior a la de inicio.")
    if p.salario_diario <= 0 or p.salario_diario_integrado <= 0:
        raise ValueError("El salario diario y el integrado deben ser mayores que cero.")

    total_dias = (fs - fi).days
    anios_totales = total_dias / 365.0
    ultimo_aniversario = aniversario_anterior(fi, fs)
    dias_ultimo_periodo = (fs - ultimo_aniversario).days
    # Si el corte coincide exactamente con un aniversario, el último periodo
    # anual se considera completado al 100%, no en cero.
    fraccion_ultimo_anio = (
        1.0 if total_dias > 0 and dias_ultimo_periodo == 0
        else max(0.0, min(dias_ultimo_periodo / 365.0, 1.0))
    )
    inicio_aguinaldo = max(fi, datetime(fs.year, 1, 1))
    dias_aguinaldo_periodo = max(0, (fs - inicio_aguinaldo).days)

    # Indemnizaciones. Los 20 días se calculan hasta la fecha efectiva de corte.
    ic = p.dias_indemnizacion * p.salario_diario_integrado
    indemnizacion_20 = 20 * p.salario_diario_integrado * anios_totales

    salario_topado = min(p.salario_diario, tope_antiguedad(fs.year))
    prima_antiguedad = 12 * salario_topado * anios_totales

    anios_cumplidos = max(0, int((ultimo_aniversario - fi).days / 365))
    sistema_vacaciones = VACACIONES_NUEVO if fs.year > 2022 else VACACIONES_ANTERIOR
    # Durante un periodo en curso se usa el nivel del año que se está trabajando.
    # En aniversario exacto se liquida al 100% el periodo que acaba de concluir.
    anio_vacacional = (
        max(anios_cumplidos - 1, 0)
        if total_dias > 0 and dias_ultimo_periodo == 0
        else anios_cumplidos
    )
    indice = min(anio_vacacional, len(sistema_vacaciones) - 1)
    dias_vacaciones = (
        p.dias_vacaciones_manual
        if p.dias_vacaciones_manual > 0
        else sistema_vacaciones[indice]
    )
    vacaciones = dias_vacaciones * p.salario_diario * fraccion_ultimo_anio
    prima_vacacional = vacaciones * p.prima_vacacional
    aguinaldo = p.dias_aguinaldo * p.salario_diario * dias_aguinaldo_periodo / 365

    dias_proporcionales = min(total_dias, 365)
    feriados = 5 * p.salario_diario * 3 * dias_proporcionales / 365
    septimos = (dias_proporcionales // 7) * p.salario_diario * 3
    # Prima dominical proporcional a semanas trabajadas, con máximo de 52.
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
    semana_fondo = 7 * p.salario_diario
    fondo_ahorro = p.fondo_ahorro * 2
    salarios_devengados = p.dias_salario_devengado * p.salario_diario

    calculados = {
        "IC": ic,
        "PA": prima_antiguedad,
        "VN": vacaciones,
        "PV": prima_vacacional,
        "AN": aguinaldo,
        "IN": indemnizacion_20,
        "DON": feriados,
        "D7N": septimos,
        "PDN": prima_dominical,
        "HX2N": horas_extra,
        "SF": semana_fondo,
        "FAC": fondo_ahorro,
    }

    resultados = {clave: valor if seleccion.get(clave, False) else 0.0
                  for clave, valor in calculados.items()}
    resultados.update({
        "Nm": p.nombre,
        "IC90": 90 * p.salario_diario_integrado,
        "IC60": 60 * p.salario_diario_integrado,
        "IC45": 45 * p.salario_diario_integrado,
        "IC30": 30 * p.salario_diario_integrado,
        "dias_relacion": total_dias,
        "anios_relacion": anios_totales,
        "salario_topado_PA": salario_topado,
    })
    resultados["total_prestaciones"] = (
        p.cantidades_expresas + salarios_devengados + sum(resultados[k] for k in calculados)
    )
    return resultados


class Aplicacion(tk.Tk):
    CAMPOS = [
        ("fecha_inicio", "Fecha de inicio (dd-mm-yyyy):"),
        ("fecha_salida", "Fecha de salida o corte (dd-mm-yyyy):"),
        ("salario_diario", "Salario diario:"),
        ("salario_integrado", "Salario diario integrado (opcional):"),
        ("cantidades_expresas", "Cantidades expresas (número o cálculo):"),
        ("fondo_ahorro", "Fondo de ahorro (sin duplicar):"),
        ("salarios_devengados", "Días de salario devengados:"),
        ("dias_indemnizacion", "Días de indemnización (base 90):"),
        ("dias_vacaciones", "Días de vacaciones manuales:"),
        ("prima_vacacional", "Prima vacacional (base 0.25):"),
        ("dias_aguinaldo", "Días de aguinaldo (base 15):"),
        ("horas_extra", "Horas extra semanales (base 9):"),
        ("nombre", "Nombre del trabajador:"),
    ]

    CONCEPTOS = [
        ("IC", "Indemnización constitucional"),
        ("PA", "Prima de antigüedad"),
        ("VN", "Vacaciones"),
        ("PV", "Prima vacacional"),
        ("AN", "Aguinaldo"),
        ("IN", "Indemnización de 20 días por año"),
        ("DON", "Días feriados"),
        ("D7N", "Séptimos días"),
        ("PDN", "Prima dominical"),
        ("HX2N", "Horas extras"),
        ("SF", "Semana de fondo"),
        ("FAC", "Fondo de ahorro duplicado"),
    ]

    def __init__(self):
        super().__init__()
        self.title("Calculadora de Prestaciones México 2026")
        self.resizable(False, False)
        self.entries = {}
        self.vars = {}
        self._crear_interfaz()

    def _crear_interfaz(self):
        marco = ttk.Frame(self, padding=12)
        marco.grid()
        for fila, (clave, etiqueta) in enumerate(self.CAMPOS):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="e", padx=4, pady=2)
            entrada = ttk.Entry(marco, width=28)
            entrada.grid(row=fila, column=1, sticky="w", padx=4, pady=2)
            self.entries[clave] = entrada

        self.entries["dias_indemnizacion"].insert(0, "90")
        self.entries["prima_vacacional"].insert(0, "0.25")
        self.entries["dias_aguinaldo"].insert(0, "15")
        self.entries["horas_extra"].insert(0, "9")

        inicio_checks = len(self.CAMPOS)
        for i, (clave, texto) in enumerate(self.CONCEPTOS):
            var = tk.IntVar(value=0)
            self.vars[clave] = var
            ttk.Checkbutton(marco, text=texto, variable=var).grid(
                row=inicio_checks + i // 2, column=i % 2, sticky="w", padx=4
            )

        fila_botones = inicio_checks + (len(self.CONCEPTOS) + 1) // 2
        ttk.Button(marco, text="Calcular", command=self.calcular).grid(
            row=fila_botones, column=0, pady=10, sticky="ew"
        )
        ttk.Button(marco, text="Importar Excel", command=self.importar_excel).grid(
            row=fila_botones, column=1, pady=10, sticky="ew"
        )

    def _parametros_desde_formulario(self):
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
            dias_indemnizacion=numero_seguro(self.entries["dias_indemnizacion"].get(), 90),
            dias_vacaciones_manual=numero_seguro(self.entries["dias_vacaciones"].get()),
            prima_vacacional=numero_seguro(self.entries["prima_vacacional"].get(), 0.25),
            dias_aguinaldo=numero_seguro(self.entries["dias_aguinaldo"].get(), 15),
            horas_extra_semanales=numero_seguro(self.entries["horas_extra"].get(), 9),
        )

    def calcular(self):
        try:
            p = self._parametros_desde_formulario()
            r = calcular_prestaciones(p, {k: bool(v.get()) for k, v in self.vars.items()})
            etiquetas = dict(self.CONCEPTOS)
            lineas = [
                f"Nombre: {r['Nm'] or '(sin nombre)'}",
                f"Antigüedad: {r['anios_relacion']:.6f} años ({r['dias_relacion']} días)",
                "",
            ]
            for clave, _ in self.CONCEPTOS:
                if self.vars[clave].get():
                    lineas.append(f"{etiquetas[clave]}: ${r[clave]:,.2f}")
            lineas.extend(["", f"TOTAL: ${r['total_prestaciones']:,.2f}"])
            messagebox.showinfo("Resultado", "\n".join(lineas))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def importar_excel(self):
        if pd is None:
            messagebox.showerror("Error", "Para importar Excel instala pandas y openpyxl.")
            return
        try:
            ruta = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
            if not ruta:
                return
            df = pd.read_excel(ruta)
            requeridas = {"Nombre", "FechaInicio", "FechaSalida", "SalarioDiario"}
            faltantes = requeridas - set(df.columns)
            if faltantes:
                raise ValueError("Faltan columnas: " + ", ".join(sorted(faltantes)))

            seleccion = {k: bool(v.get()) for k, v in self.vars.items()}
            salida = []
            for _, fila in df.iterrows():
                fi = pd.to_datetime(fila["FechaInicio"], errors="coerce", dayfirst=True)
                fs = pd.to_datetime(fila["FechaSalida"], errors="coerce", dayfirst=True)
                if pd.isna(fi) or pd.isna(fs):
                    raise ValueError(f"Fecha inválida para {fila['Nombre']}")
                sd = float(fila["SalarioDiario"])
                sdi = float(fila.get("SalarioDiarioIntegrado", sd) or sd)
                p = Parametros(
                    nombre=str(fila["Nombre"]),
                    fecha_inicio=fi.to_pydatetime(),
                    fecha_salida=fs.to_pydatetime(),
                    salario_diario=sd,
                    salario_diario_integrado=sdi,
                )
                r = calcular_prestaciones(p, seleccion)
                salida.append({
                    "Nombre": r["Nm"],
                    "TotalPrestaciones": r["total_prestaciones"],
                    "IndemnizacionConstitucional": r["IC"],
                    "PrimaAntiguedad": r["PA"],
                    "Indemnizacion20Dias": r["IN"],
                    "Vacaciones": r["VN"],
                    "PrimaVacacional": r["PV"],
                    "Aguinaldo": r["AN"],
                    "PrimaDominical": r["PDN"],
                    "HorasExtras": r["HX2N"],
                })

            destino = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")]
            )
            if destino:
                pd.DataFrame(salida).round(2).to_excel(destino, index=False)
                messagebox.showinfo("Éxito", f"Resultados guardados en:\n{destino}")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


if __name__ == "__main__":
    Aplicacion().mainloop()
