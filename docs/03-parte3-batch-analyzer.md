# 03 — Parte 3: Analizador de Lotes (Algoritmos y Aplicación)

Ensambla Parte 1 + Parte 2 para procesar el CSV de datos "sucios" (`Desafío técnico — Xpendit/gastos_historicos.csv`, datos migrados de un sistema antiguo). Ver `04-csv-data-notes.md`.

## Tareas
1. Procesar todas las filas: convertir monto a USD (cliente Parte 2) + aplicar reglas de política (motor Parte 1).
2. **Detección de anomalías** — implementar AL MENOS 2 (conviene las 2; este dataset solo puebla la primera):
   - **Duplicados exactos**: gastos con `monto`, `moneda` y `fecha` idénticos. Caso real: g_042/g_043/g_044 = Bruno 90 USD 2026-06-06. Decidir y documentar el criterio: ¿(monto,moneda,fecha) puro como dice el spec, o incluir empleado? (algunos colisionan entre empleados distintos).
   - **Montos negativos**: gastos con montos erróneos (<0). En este dataset hay **0** — implementar la lógica igual y reportar que no se hallaron.
3. **Optimización (Bonus) — evitar N+1**: la solución naive llama la API 1 vez por fila. La optimizada **agrupa por fecha única → 1 llamada por fecha** y cachea. Implementarlo y explicarlo suma.

## Entregables
- Código del script (ej. `python analizar.py`).
- **`ANALISIS.md`** que responda: (a) desglose por estado (ej "35 APROBADOS, 10 PENDIENTES, 5 RECHAZADOS"), (b) anomalías encontradas con ejemplos concretos, (c) [Bonus] explicación de la optimización N+1.
- **Video ≤ 1 minuto** resumiendo hallazgos.
