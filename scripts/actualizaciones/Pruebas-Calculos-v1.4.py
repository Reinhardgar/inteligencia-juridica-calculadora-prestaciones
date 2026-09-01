import unittest
from datetime import datetime
from calculadora_prestaciones_consolidada import Parametros, calcular_prestaciones

class PruebasV14(unittest.TestCase):
    def calcular(self, fi, fs, sd=800, horas=9, seleccion=None):
        p = Parametros("PRUEBA", fi, fs, sd, sd, horas_extra_semanales=horas)
        return calcular_prestaciones(p, seleccion or {})

    def test_prima_dominical_26_semanas(self):
        r = self.calcular(datetime(2026,1,1), datetime(2026,7,2), seleccion={"PDN": True})
        semanas = min((datetime(2026,7,2)-datetime(2026,1,1)).days/7, 52)
        self.assertAlmostEqual(r["PDN"], 800*.25*semanas, places=7)

    def test_prima_dominical_tope_52(self):
        r = self.calcular(datetime(2024,1,1), datetime(2026,1,1), seleccion={"PDN": True})
        self.assertAlmostEqual(r["PDN"], 800*.25*52, places=7)

    def test_horas_nueve_dobles(self):
        r = self.calcular(datetime(2025,1,1), datetime(2026,1,1), horas=9, seleccion={"HX2N": True})
        self.assertAlmostEqual(r["HX2N"], 9*2*(800/8)*52, places=7)

    def test_horas_doce_mixtas(self):
        r = self.calcular(datetime(2025,1,1), datetime(2026,1,1), horas=12, seleccion={"HX2N": True})
        esperado = ((9*2)+(3*3))*(800/8)*52
        self.assertAlmostEqual(r["HX2N"], esperado, places=7)

    def test_vacaciones_aniversario_no_cero(self):
        r = self.calcular(datetime(2025,1,1), datetime(2026,1,1), seleccion={"VN": True})
        self.assertAlmostEqual(r["VN"], 12*800, places=7)

if __name__ == "__main__":
    unittest.main(verbosity=2)
