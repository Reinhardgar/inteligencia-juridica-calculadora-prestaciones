import ast
import operator
from dataclasses import dataclass, field
from datetime import datetime

TOPES_DOBLE_SALARIO_MINIMO = {2017:168.94,2018:176.72,2019:205.36,2020:246.44,2021:283.40,2022:345.74,2023:414.88,2024:496.00,2025:557.60,2026:630.08}
VACACIONES_NUEVO=[12,14,16,18,20,22,22,22,22,22,24,24,24,24,24,26,26,26,26,26,28,28,28,28,28,30,30,30,30,30,32,32,32,32,32]
VACACIONES_ANTERIOR=[6,8,10,12,14,14,14,14,14,16,16,16,16,16,18,18,18,18,18,20,20,20,20,20,22,22,22,22,22,24,24,24,24,24]
_OPERADORES={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.USub:operator.neg,ast.UAdd:operator.pos}

def numero_seguro(texto,predeterminado=0.0):
    if texto is None or str(texto).strip()=='': return float(predeterminado)
    nodo=ast.parse(str(texto).replace(',',''),mode='eval')
    def ev(n):
        if isinstance(n,ast.Expression): return ev(n.body)
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)): return float(n.value)
        if isinstance(n,ast.BinOp) and type(n.op) in _OPERADORES: return _OPERADORES[type(n.op)](ev(n.left),ev(n.right))
        if isinstance(n,ast.UnaryOp) and type(n.op) in _OPERADORES: return _OPERADORES[type(n.op)](ev(n.operand))
        raise ValueError('Solo se permiten números y operaciones +, -, * y /.')
    valor=float(ev(nodo))
    if valor<0: raise ValueError('Los importes y días no pueden ser negativos.')
    return valor

def parsear_fecha(texto): return datetime.strptime(str(texto).strip(),'%d-%m-%Y')
def aniversario_anterior(fi,fs):
    try: a=fi.replace(year=fs.year)
    except ValueError: a=fi.replace(year=fs.year,day=28)
    if a>fs:
        try: a=fi.replace(year=fs.year-1)
        except ValueError: a=fi.replace(year=fs.year-1,day=28)
    return a
def tope_antiguedad(anio):
    if anio not in TOPES_DOBLE_SALARIO_MINIMO: raise ValueError(f'No existe tope de prima de antigüedad configurado para {anio}.')
    return TOPES_DOBLE_SALARIO_MINIMO[anio]
def tabla_vacaciones(fecha): return VACACIONES_NUEVO if fecha.year>2022 else VACACIONES_ANTERIOR
def dias_tabla(indice,fecha):
    t=tabla_vacaciones(fecha); return t[min(max(indice,0),len(t)-1)]

@dataclass
class Parametros:
    nombre:str; fecha_inicio:datetime; fecha_salida:datetime; salario_diario:float; salario_diario_integrado:float
    conceptos_expresos:list=field(default_factory=list)
    fondo_ahorro:float=0.0; dias_salario_devengado:float=0.0; dias_indemnizacion:float=90.0
    dias_vacaciones_pendientes_manual:float=0.0
    dias_vacaciones_proporcionales_manual:float=0.0
    prima_vacacional:float=0.25; dias_aguinaldo:float=15.0; horas_extra_semanales:float=9.0

def calcular_prestaciones(p,seleccion):
    fi,fs=p.fecha_inicio,p.fecha_salida
    if fs<fi: raise ValueError('La fecha de salida no puede ser anterior a la de ingreso.')
    if p.salario_diario<=0 or p.salario_diario_integrado<=0: raise ValueError('Los salarios deben ser mayores que cero.')
    total_dias=(fs-fi).days; anios=total_dias/365.0; ua=aniversario_anterior(fi,fs)
    dias_periodo=max(0,(fs-ua).days); fraccion=min(dias_periodo/365.0,1.0)
    anios_cumplidos=max(0,fs.year-fi.year-((fs.month,fs.day)<(fi.month,fi.day)))
    # Periodo en curso: el que comienza en el último aniversario. Antes del primero usa nivel 1.
    nivel_proporcional=max(anios_cumplidos,0)
    dias_base_prop=dias_tabla(nivel_proporcional,fs)
    dias_prop=(p.dias_vacaciones_proporcionales_manual if p.dias_vacaciones_proporcionales_manual>0 else dias_base_prop*fraccion)
    # Último periodo concluido: existe a partir del primer aniversario y se valora al 100%.
    dias_base_pend=dias_tabla(max(anios_cumplidos-1,0),ua)
    dias_pend=(p.dias_vacaciones_pendientes_manual if p.dias_vacaciones_pendientes_manual>0 else (dias_base_pend if anios_cumplidos>=1 else 0.0))
    vacaciones_prop=dias_prop*p.salario_diario; vacaciones_pend=dias_pend*p.salario_diario
    prima_vac=(vacaciones_prop+vacaciones_pend)*p.prima_vacacional
    inicio_ag=max(fi,datetime(fs.year,1,1)); dias_ag=max(0,(fs-inicio_ag).days)
    semanas=min(total_dias/7.0,52.0); hd=min(p.horas_extra_semanales,9.0); ht=max(p.horas_extra_semanales-9.0,0.0)
    valores={'IC':p.dias_indemnizacion*p.salario_diario_integrado,'IN':20*p.salario_diario_integrado*anios,
      'PA':12*min(p.salario_diario,tope_antiguedad(fs.year))*anios,'VNP':vacaciones_prop,'VPN':vacaciones_pend,
      'PV':prima_vac,'AN':p.dias_aguinaldo*p.salario_diario*dias_ag/365,'DON':5*p.salario_diario*3*min(total_dias,365)/365,
      'D7N':(min(total_dias,365)//7)*p.salario_diario*3,'PDN':p.salario_diario*.25*semanas,
      'HX2N':((hd*2)+(ht*3))*(p.salario_diario/8)*semanas,'SF':7*p.salario_diario,'FAC':p.fondo_ahorro*2,
      'SDV':p.dias_salario_devengado*p.salario_diario}
    r={k:(v if seleccion.get(k,False) else 0.0) for k,v in valores.items()}
    detalles=[]
    for x in p.conceptos_expresos:
        concepto=str(x.get('concepto','')).strip(); monto=numero_seguro(x.get('monto',0))
        if concepto and monto>0: detalles.append({'concepto':concepto,'monto':monto})
    r.update({'Nm':p.nombre,'dias_relacion':total_dias,'anios_relacion':anios,'salario_topado_PA':min(p.salario_diario,tope_antiguedad(fs.year)),
              'dias_vacaciones_proporcionales':dias_prop,'dias_vacaciones_pendientes':dias_pend,'conceptos_expresos':detalles})
    r['total_prestaciones']=sum(r[k] for k in valores)+sum(x['monto'] for x in detalles)
    return r
