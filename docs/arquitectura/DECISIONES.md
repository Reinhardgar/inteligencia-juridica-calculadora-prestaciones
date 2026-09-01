# Decisiones de arquitectura

1. El motor de cÃ¡lculo permanece separado de la interfaz.
2. Las reglas legales parametrizables deberÃ¡n salir progresivamente del cÃ³digo hacia configuraciÃ³n versionada.
3. Dataverse serÃ¡ la fuente operativa futura; la calculadora no almacenarÃ¡ credenciales ni acceso directo incrustado.
4. Cada versiÃ³n estable debe incluir pruebas, changelog e instalador trazable.
