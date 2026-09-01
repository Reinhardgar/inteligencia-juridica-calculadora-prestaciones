# Calculadora Jurídico-Laboral

Módulo de **Inteligencia Jurídica** para cuantificar prestaciones laborales y apoyar la estimación del monto reclamado al presentar una demanda.

## Versión estable

1.5.1

## Funcionalidades principales

- Cálculo de prestaciones laborales con desglose por concepto.
- Salarios devengados incorporados automáticamente cuando existen días capturados.
- Cantidades expresas con concepto y monto.
- Vacaciones proporcionales del periodo en curso.
- Vacaciones pendientes del último periodo concluido.
- Pruebas automatizadas y generación de instalador para Windows.

## Estructura

- `src/motor`: reglas y operaciones de cálculo.
- `src/interfaz`: aplicación de escritorio.
- `tests`: pruebas automatizadas.
- `assets`: logotipo e iconos.
- `packaging`: compilación con PyInstaller e Inno Setup.
- `docs`: decisiones técnicas y jurídicas.
- `releases`: instaladores aprobados por versión.

## Validación

Los resultados son auxiliares y deben revisarse conforme a los hechos, documentos y criterio jurídico aplicable a cada expediente.

## Seguridad

No se deben almacenar contraseñas, tokens, expedientes, datos personales ni bases productivas en este repositorio.
