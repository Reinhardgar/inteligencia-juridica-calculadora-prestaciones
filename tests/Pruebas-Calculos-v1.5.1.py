import unittest
from datetime import datetime
from calculadora_prestaciones_consolidada import Parametros, calcular_prestaciones

class PruebasV151(unittest.TestCase):
    def calcular(self, fi, fs, sd=800, horas=9, seleccion=None, **kwargs):
        p = Parametros(
            nombre='PRUEBA', fecha_inicio=fi, fecha_salida=fs,
            salario_diario=sd, salario_diario_integrado=sd,
            horas_extra_semanales=horas, **kwargs
        )
        return calcular_prestaciones(p, seleccion or {})

    def test_primer_aniversario_pendientes_12_y_proporcionales_0(self):
        r = self.calcular(
            datetime(2025, 1, 1), datetime(2026, 1, 1),
            seleccion={'VPN': True, 'VNP': True}
        )
        self.assertAlmostEqual(r['VPN'], 12 * 800, places=7)
        self.assertAlmostEqual(r['VNP'], 0, places=7)
        self.assertAlmostEqual(r['dias_vacaciones_pendientes'], 12, places=7)
        self.assertAlmostEqual(r['dias_vacaciones_proporcionales'], 0, places=7)

    def test_segundo_periodo_proporcional_y_primero_pendiente(self):
        fi = datetime(2024, 1, 1)
        fs = datetime(2025, 7, 2)
        fraccion = (fs - datetime(2025, 1, 1)).days / 365
        r = self.calcular(fi, fs, seleccion={'VPN': True, 'VNP': True})
        self.assertAlmostEqual(r['VPN'], 12 * 800, places=7)
        self.assertAlmostEqual(r['VNP'], 14 * fraccion * 800, places=7)

    def test_reemplazos_manuales_de_vacaciones(self):
        r = self.calcular(
            datetime(2024, 1, 1), datetime(2025, 7, 2),
            seleccion={'VPN': True, 'VNP': True},
            dias_vacaciones_pendientes_manual=4,
            dias_vacaciones_proporcionales_manual=3.5
        )
        self.assertAlmostEqual(r['VPN'], 4 * 800, places=7)
        self.assertAlmostEqual(r['VNP'], 3.5 * 800, places=7)

    def test_prima_vacacional_sobre_ambas_vacaciones(self):
        r = self.calcular(
            datetime(2024, 1, 1), datetime(2025, 7, 2),
            seleccion={'VPN': True, 'VNP': True, 'PV': True},
            dias_vacaciones_pendientes_manual=4,
            dias_vacaciones_proporcionales_manual=3.5
        )
        self.assertAlmostEqual(r['PV'], (4 + 3.5) * 800 * 0.25, places=7)

    def test_salarios_devengados(self):
        r = self.calcular(
            datetime(2026, 1, 1), datetime(2026, 2, 1),
            seleccion={'SDV': True}, dias_salario_devengado=6
        )
        self.assertAlmostEqual(r['SDV'], 6 * 800, places=7)

    def test_cantidades_expresas_se_suman_y_conservan_concepto(self):
        r = self.calcular(
            datetime(2026, 1, 1), datetime(2026, 2, 1),
            seleccion={}, conceptos_expresos=[
                {'concepto': 'Bono contractual', 'monto': '1200+300'},
                {'concepto': 'Comisión pendiente', 'monto': '2500/2'}
            ]
        )
        self.assertEqual(r['conceptos_expresos'][0]['concepto'], 'Bono contractual')
        self.assertAlmostEqual(r['total_prestaciones'], 2750, places=7)

    def test_horas_12_mixtas(self):
        r = self.calcular(
            datetime(2025, 1, 1), datetime(2026, 1, 1),
            horas=12, seleccion={'HX2N': True}
        )
        self.assertAlmostEqual(r['HX2N'], ((9*2)+(3*3))*(800/8)*52, places=7)

    def test_prima_dominical_menor_un_ano(self):
        fi = datetime(2026, 1, 1); fs = datetime(2026, 7, 2)
        r = self.calcular(fi, fs, seleccion={'PDN': True})
        self.assertAlmostEqual(r['PDN'], 800*.25*((fs-fi).days/7), places=7)

if __name__ == '__main__':
    unittest.main(verbosity=2)
