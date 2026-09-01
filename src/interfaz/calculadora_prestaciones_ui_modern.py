import json, os, sys, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from calculadora_prestaciones_consolidada import Parametros, calcular_prestaciones, numero_seguro, parsear_fecha
APP_NAME='Calculadora Jurídico-Laboral'; APP_VERSION='1.5.1'
def resource_path(n): return os.path.join(getattr(sys,'_MEIPASS',os.path.dirname(os.path.abspath(__file__))),n)
CONCEPTOS=[('IC','Indemnización constitucional'),('IN','20 días por año'),('PA','Prima de antigüedad'),('VNP','Vacaciones proporcionales'),('VPN','Vacaciones pendientes'),('PV','Prima vacacional'),('AN','Aguinaldo'),('PDN','Prima dominical'),('HX2N','Horas extras'),('DON','Días feriados'),('D7N','Séptimos días'),('SF','Semana de fondo')]
class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title(f'{APP_NAME} {APP_VERSION}'); self.geometry('1180x760'); self.configure(bg='#f4f7fb'); self.minsize(1050,680)
  try:self.iconbitmap(resource_path('calculadora_despacho_(1).ico'))
  except:pass
  self.e={}; self.vars={k:tk.BooleanVar() for k,_ in CONCEPTOS}; self.extras=[]; self.ultimo=None; self._ui()
 def _ui(self):
  h=tk.Frame(self,bg='#102a43',height=82); h.pack(fill='x'); h.pack_propagate(False)
  tk.Label(h,text=APP_NAME,font=('Segoe UI Semibold',20),fg='white',bg='#102a43').pack(anchor='w',padx=24,pady=(14,0))
  tk.Label(h,text='Cálculo trazable y preparado para revisión jurídica',font=('Segoe UI',10),fg='#d9e8f5',bg='#102a43').pack(anchor='w',padx=25)
  body=tk.Frame(self,bg='#f4f7fb'); body.pack(fill='both',expand=True,padx=18,pady=18); body.grid_columnconfigure(0,weight=1); body.grid_columnconfigure(1,weight=1); body.grid_rowconfigure(0,weight=1)
  L=tk.Frame(body,bg='white',padx=18,pady=16); R=tk.Frame(body,bg='white',padx=18,pady=16); L.grid(row=0,column=0,sticky='nsew',padx=(0,8)); R.grid(row=0,column=1,sticky='nsew',padx=(8,0)); L.grid_columnconfigure(1,weight=1); R.grid_columnconfigure(0,weight=1); R.grid_rowconfigure(3,weight=1)
  tk.Label(L,text='Datos del expediente',font=('Segoe UI Semibold',12),bg='white',fg='#102a43').grid(row=0,column=0,columnspan=2,sticky='w',pady=(0,8))
  campos=[('nombre','Nombre del trabajador'),('fi','Fecha de Ingreso'),('fs','Fecha de salida o corte'),('sd','Salario diario (admite cálculos)'),('sdi','Salario diario integrado (Opcional)'),('fondo','Fondo de ahorro sin duplicar'),('dev','Días de salario devengados')]
  for i,(k,t) in enumerate(campos,1): tk.Label(L,text=t,bg='white').grid(row=i,column=0,sticky='w',pady=5); self.e[k]=ttk.Entry(L); self.e[k].grid(row=i,column=1,sticky='ew',pady=5,padx=(12,0))
  self.e['fondo'].insert(0,'0'); self.e['dev'].insert(0,'0')
  xfr=tk.Frame(L,bg='white'); xfr.grid(row=8,column=0,columnspan=2,sticky='ew',pady=8); xfr.grid_columnconfigure(0,weight=1)
  tk.Label(xfr,text='Cantidades expresas',font=('Segoe UI Semibold',10),bg='white').grid(row=0,column=0,sticky='w'); ttk.Button(xfr,text='+',width=4,command=self.add_extra).grid(row=0,column=1)
  self.extra_lbl=tk.Label(xfr,text='Sin conceptos adicionales',bg='white',fg='#607080',anchor='w'); self.extra_lbl.grid(row=1,column=0,columnspan=2,sticky='ew')
  par=ttk.LabelFrame(L,text='Parámetros jurídicos y de cálculo',padding=10); par.grid(row=9,column=0,columnspan=2,sticky='ew',pady=8)
  pars=[('ind','Días indemnización','90'),('vacp','Vacaciones proporcionales','0'),('vacpend','Vacaciones pendientes','0'),('pv','Prima vacacional','0.25'),('ag','Días aguinaldo','15'),('hx','Horas extra/semana','9')]
  for i,(k,t,v) in enumerate(pars): tk.Label(par,text=t).grid(row=i//2,column=(i%2)*2,sticky='w',padx=(0,5),pady=4); self.e[k]=ttk.Entry(par,width=12); self.e[k].grid(row=i//2,column=(i%2)*2+1,sticky='w',padx=(0,14)); self.e[k].insert(0,v)
  bf=tk.Frame(L,bg='white'); bf.grid(row=10,column=0,columnspan=2,sticky='ew',pady=10); ttk.Button(bf,text='Calcular',command=self.calc).pack(side='left'); ttk.Button(bf,text='Limpiar',command=self.clear).pack(side='left',padx=8)
  tk.Label(R,text='Prestaciones a incluir',font=('Segoe UI Semibold',12),bg='white',fg='#102a43').grid(row=0,column=0,sticky='w')
  cf=tk.Frame(R,bg='white'); cf.grid(row=1,column=0,sticky='ew',pady=8)
  for i,(k,t) in enumerate(CONCEPTOS): ttk.Checkbutton(cf,text=t,variable=self.vars[k]).grid(row=i//2,column=i%2,sticky='w',padx=(0,18),pady=3)
  self.tree=ttk.Treeview(R,columns=('c','m'),show='headings'); self.tree.heading('c',text='Concepto'); self.tree.heading('m',text='Importe'); self.tree.column('m',anchor='e',width=140); self.tree.grid(row=3,column=0,sticky='nsew',pady=8)
  self.total=tk.Label(R,text='TOTAL: $0.00',font=('Segoe UI Semibold',14),bg='white',fg='#102a43'); self.total.grid(row=4,column=0,sticky='e')
  ttk.Button(R,text='Copiar resumen',command=self.copy_summary).grid(row=5,column=0,sticky='e',pady=8)
 def add_extra(self):
  w=tk.Toplevel(self); w.title('Agregar cantidad expresa'); w.transient(self); w.grab_set(); w.resizable(False,False)
  tk.Label(w,text='Concepto').grid(row=0,column=0,padx=12,pady=8,sticky='w'); c=ttk.Entry(w,width=35); c.grid(row=0,column=1,padx=12,pady=8)
  tk.Label(w,text='Monto (admite cálculos)').grid(row=1,column=0,padx=12,pady=8,sticky='w'); m=ttk.Entry(w,width=35); m.grid(row=1,column=1,padx=12,pady=8)
  def ok():
   try:
    concepto=c.get().strip(); monto=numero_seguro(m.get())
    if not concepto or monto<=0: raise ValueError('Capture concepto y monto mayor que cero.')
    self.extras.append({'concepto':concepto,'monto':monto}); self.extra_lbl.config(text=f'{len(self.extras)} concepto(s), total ${sum(x["monto"] for x in self.extras):,.2f}'); w.destroy()
   except Exception as ex: messagebox.showerror('Revise los datos',str(ex),parent=w)
  ttk.Button(w,text='Agregar',command=ok).grid(row=2,column=0,columnspan=2,pady=12); c.focus_set()
 def params(self):
  sd=numero_seguro(self.e['sd'].get()); sdi=numero_seguro(self.e['sdi'].get(),sd)
  return Parametros(self.e['nombre'].get().strip(),parsear_fecha(self.e['fi'].get()),parsear_fecha(self.e['fs'].get()),sd,sdi,list(self.extras),numero_seguro(self.e['fondo'].get()),numero_seguro(self.e['dev'].get()),numero_seguro(self.e['ind'].get(),90),numero_seguro(self.e['vacpend'].get()),numero_seguro(self.e['vacp'].get()),numero_seguro(self.e['pv'].get(),.25),numero_seguro(self.e['ag'].get(),15),numero_seguro(self.e['hx'].get(),9))
 def calc(self):
  try:
   p=self.params(); sel={k:v.get() for k,v in self.vars.items()}; sel['FAC']=p.fondo_ahorro>0; sel['SDV']=p.dias_salario_devengado>0
   r=calcular_prestaciones(p,sel); self.ultimo=r
   for x in self.tree.get_children(): self.tree.delete(x)
   labels=dict(CONCEPTOS)|{'FAC':'Fondo de ahorro','SDV':'Salarios devengados'}
   for k in [x[0] for x in CONCEPTOS]+['FAC','SDV']:
    if sel.get(k): self.tree.insert('', 'end',values=(labels[k],f'${r[k]:,.2f}'))
   for x in r['conceptos_expresos']: self.tree.insert('','end',values=(x['concepto'],f'${x["monto"]:,.2f}'))
   self.total.config(text=f'TOTAL: ${r["total_prestaciones"]:,.2f}'); self.clipboard_clear(); self.clipboard_append(f'{r["total_prestaciones"]:.2f}'); self.update()
  except Exception as ex: messagebox.showerror('Revise los datos',str(ex))
 def copy_summary(self):
  if not self.ultimo:return
  lines=[f'{self.tree.item(i,"values")[0]}: {self.tree.item(i,"values")[1]}' for i in self.tree.get_children()]+[self.total.cget('text')]; self.clipboard_clear(); self.clipboard_append('\n'.join(lines))
 def clear(self):
  for e in self.e.values(): e.delete(0,'end')
  for v in self.vars.values():v.set(False)
  self.extras=[]; self.extra_lbl.config(text='Sin conceptos adicionales')
  for x in self.tree.get_children():self.tree.delete(x)
  self.total.config(text='TOTAL: $0.00')
if __name__=='__main__': App().mainloop()
