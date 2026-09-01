import unittest
from datetime import datetime
from calculadora_prestaciones_consolidada import Parametros, calcular_prestaciones

class PruebasV141(unittest.TestCase):
    def c(self, fi, fs, sd=800, horas=9, sel=None):
        p=Parametros("PRUEBA",fi,fs,sd,sd,horas_extra_semanales=horas)
        return calcular_prestaciones(p,sel or {})
    def test_primer_aniversario_12_dias(self):
        r=self.c(datetime(2025,1,1),datetime(2026,1,1),sel={"VN":True})
        self.assertAlmostEqual(r["VN"],12*800,places=7)
    def test_segundo_periodo_al_50_por_ciento(self):
        fi=datetime(2024,1,1); fs=datetime(2025,7,2)
        r=self.c(fi,fs,sel={"VN":True})
        ua=datetime(2025,1,1)
        esperado=14*800*((fs-ua).days/365)
        self.assertAlmostEqual(r["VN"],esperado,places=7)
    def test_prima_dominical_menor_un_ano(self):
        fi=datetime(2026,1,1); fs=datetime(2026,7,2)
        r=self.c(fi,fs,sel={"PDN":True})
        self.assertAlmostEqual(r["PDN"],800*.25*((fs-fi).days/7),places=7)
    def test_horas_12_mixtas(self):
        r=self.c(datetime(2025,1,1),datetime(2026,1,1),horas=12,sel={"HX2N":True})
        self.assertAlmostEqual(r["HX2N"],((9*2)+(3*3))*(800/8)*52,places=7)
if __name__ == "__main__": unittest.main(verbosity=2)
