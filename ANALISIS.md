# Análisis del lote `gastos_historicos.csv`

Resultados de procesar los **50 gastos** del CSV con el motor de reglas y tasas de cambio
**históricas reales** (Open Exchange Rates) del día de cada gasto.

> Reproducir: `python -m expense_engine.cli.analyze "Desafío técnico — Xpendit/gastos_historicos.csv" --reference-date 2026-06-16`
> La antigüedad se calcula contra la **fecha de referencia 2026-06-16** (fija para que el análisis sea reproducible).

## 1. Desglose por estado

| Estado | Gastos |
|-----------|:------:|
| APROBADO  | 13 |
| PENDIENTE | 13 |
| RECHAZADO | 24 |
| **Total** | **50** |

La mayoría de los RECHAZADO se debe a la **antigüedad**: con fecha de referencia 2026-06-16,
muchos gastos del CSV (de fines de 2025 y comienzos de 2026) superan los 60 días y se rechazan
automáticamente. Otros RECHAZADO provienen de la **regla cruzada** (core_engineering + food) y
de exceder el límite de categoría.

Ejemplos representativos:
- `g_001` (food 50 USD, 15 días) → **APROBADO**.
- `g_002` (food 120 USD) → **PENDIENTE** — excede el límite aprobado de food (100 < 120 ≤ 150).
- `g_011` (food, core_engineering) → **RECHAZADO** — categoría prohibida para ese centro de costo.
- `g_023` (lodging, 2025-12-31, ~167 días) → **RECHAZADO** — por antigüedad.
- `g_007` (1.750 MXN) y `g_010` (92 EUR) → **PENDIENTE** con **dos alertas** (antigüedad + categoría):
  al convertir con la tasa real del día superan los 100 USD de food (≈101 y ≈108 USD).

## 2. Anomalías detectadas

Se implementaron las dos anomalías del enunciado.

### Duplicados exactos (mismo monto + moneda + fecha): 7 grupos

Aplicando el criterio literal del enunciado (monto, moneda, fecha). Conviene distinguir dos casos:

**Mismo empleado** — señal fuerte de doble rendición (un mismo gasto cargado varias veces):
| Monto | Fecha | Gastos | Empleado |
|-------|-------|--------|----------|
| 90 USD | 2026-06-06 | `g_042`, `g_043`, `g_044` | Bruno Soto (×3) |
| 130 EUR | 2026-04-22 | `g_038`, `g_050` | Carla Mora |
| 150 USD | 2026-03-13 | `g_039`, `g_047` | David Paz |

**Empleados distintos** — probablemente coincidencia (montos de viático estándar repetidos), no fraude:
| Monto | Fecha | Gastos | Empleados |
|-------|-------|--------|-----------|
| 50 USD | 2026-06-01 | `g_001`, `g_011` | Bruno Soto / Ana Reyes |
| 120 USD | 2026-05-27 | `g_002`, `g_012` | Bruno Soto / Ana Reyes |
| 120 USD | 2026-03-13 | `g_025`, `g_029` | Bruno Soto / Ana Reyes |
| 70 USD | 2026-06-01 | `g_036`, `g_041` | Bruno Soto / Eva Luna |

> Nota de diseño: el detector usa el criterio literal del enunciado (monto+moneda+fecha). En un
> sistema real, el duplicado de mayor confianza es el del **mismo empleado**; el criterio se podría
> endurecer agregando `empleado_id` a la clave. Lo dejamos configurable a nivel de diseño y aquí
> reportamos ambos para transparencia.

### Montos negativos: 0

No se encontraron montos negativos en este dataset. La lógica de detección está implementada y
probada igualmente (reportaría los gastos con monto < 0 si existieran).

## 3. (Bonus) Optimización de llamadas a la API — evitar N+1

Una solución naive convierte cada gasto haciendo **una llamada a la API por fila** → 50 llamadas.

Como las tasas de cambio son **por fecha** (no por gasto), agrupamos por **fecha única**: el cliente
`OpenExchangeRatesClient` **cachea en memoria las tasas de cada fecha**, de modo que la primera vez
que aparece una fecha hace la llamada HTTP y las siguientes la reutilizan.

En este lote:

| | Llamadas a la API |
|---|:---:|
| Naive (1 por gasto) | 50 |
| Optimizado (1 por fecha única) | **25** |
| Ahorro | 25 (50%) |

La optimización vive en la capa de infraestructura (el cliente), de forma transparente: el
normalizador llama `convert` una vez por gasto y el cache se encarga del resto. Esto mantiene el
código de aplicación simple y la optimización encapsulada donde corresponde.
