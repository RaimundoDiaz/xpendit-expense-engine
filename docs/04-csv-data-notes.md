# 04 — Notas del gastos_historicos.csv

Archivo: `Desafío técnico — Xpendit/gastos_historicos.csv` — **49 filas de datos** (50 líneas con header).

**Columnas**: `gasto_id, empleado_id, empleado_nombre, empleado_apellido, empleado_cost_center, categoria, monto, moneda, fecha`. Nota: el cost_center viene en cada fila del CSV, no en una tabla de empleados aparte.

**Empleados (5)**: e_001 Ana Reyes (core_engineering), e_002 Bruno Soto (sales_team), e_003 Carla Mora (marketing), e_004 David Paz (finance), e_005 Eva Luna (sales_team).

**Monedas**: USD (39), MXN (4), CLP (4), EUR (3) → la conversión a USD (Parte 2) es necesaria para CLP/MXN/EUR.

**Categorías**: food (22), transport (8), software (7), other (7), lodging (6). La política ejemplo solo define límites para `food` y `transport`; software/other/lodging no tienen límite → caen en "por defecto = PENDIENTE" salvo que se amplíe la política.

**Cost centers**: sales_team (21), core_engineering (11), finance (9), marketing (9).

**Rango de fechas**: 2025-12-31 a 2026-06-13. Con "hoy" = 2026-06-16: varios gastos superan 60 días (2025-12 / 2026-01 → RECHAZADO por antigüedad) y muchos caen 31-60 días (PENDIENTE). Considerar si "hoy" se fija o se calcula en runtime (fijar una fecha de referencia hace el análisis reproducible — documentarlo).

## Anomalías presentes
- **Duplicados exactos: SÍ.** Más claro: g_042/g_043/g_044 = Bruno 90 USD 2026-06-06 (mismo empleado, triple). Otros pares (monto,moneda,fecha) idénticos: 120/USD/2026-05-27, 130/EUR/2026-04-22, 150/USD/2026-03-13, 50/USD/2026-06-01, 70/USD/2026-06-01, 120/USD/2026-03-13. OJO: algunos colisionan entre empleados distintos (ej. 50 USD 2026-06-01 = Bruno g_001 + Ana g_011). Definir y documentar el criterio en ANALISIS.md.
- **Montos negativos: NO hay** (0 filas con monto<0). Implementar la detección igual y reportar 0 instancias.

## core_engineering + food (Regla 3 → RECHAZADO)
Ana (core_engineering) tiene gastos food: g_011, g_012, g_013, g_029 → deben salir RECHAZADO por regla cruzada.
