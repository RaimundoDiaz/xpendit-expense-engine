# 01 — Parte 1: Motor de Reglas (Lógica Pura)

Núcleo del validador de gastos. **CRÍTICO**: en esta parte toda la info externa (tasas de cambio) debe estar **mockeada o inyectada**. El motor **NO hace ninguna llamada de red**. Devuelve 3 estados: `APROBADO`, `PENDIENTE`, `RECHAZADO`.

## Modelos
- **Gasto**: `id`, `monto` (number), `moneda` (string, ej "CLP"), `fecha` (string ISO ej "2025-10-20"), `categoria` (string: "food", "transport", "software", …).
- **Empleado**: `id`, `nombre`, `apellido`, `cost_center` (string: "sales_team", "core_engineering", …).
- **Politica**: objeto data-driven con las reglas. Ejemplo:
```json
{
  "moneda_base": "USD",
  "limite_antiguedad": { "pendiente_dias": 30, "rechazado_dias": 60 },
  "limites_por_categoria": {
    "food": { "aprobado_hasta": 100, "pendiente_hasta": 150 },
    "transport": { "aprobado_hasta": 200, "pendiente_hasta": 200 }
  },
  "reglas_centro_costo": [
    { "cost_center": "core_engineering", "categoria_prohibida": "food" }
  ]
}
```

## Reglas (montos evaluados en moneda_base = USD)
| Regla | Condición | Acción | Alerta |
|---|---|---|---|
| 1 Antigüedad | 0 ≤ días ≤ 30 | APROBADO | — |
| 1 Antigüedad | 31 ≤ días ≤ 60 | PENDIENTE | `LIMITE_ANTIGUEDAD` "Gasto excede los 30 días. Requiere revisión." |
| 1 Antigüedad | días > 60 | RECHAZADO | `LIMITE_ANTIGUEDAD` |
| 2 Límite categoría | monto ≤ aprobado_hasta | APROBADO | — |
| 2 Límite categoría | aprobado_hasta < monto ≤ pendiente_hasta | PENDIENTE | "Requiere revisión" |
| 2 Límite categoría | monto > pendiente_hasta | RECHAZADO | "Excede límite aprobado" |
| 3 Regla cruzada | cost_center="core_engineering" AND categoria="food" | RECHAZADO | `POLITICA_CENTRO_COSTO` "El C.C. 'core_engineering' no puede reportar 'food'." |

`días` = hoy − fecha del gasto.

## Resolución de estado final (prioridad)
1. Si CUALQUIER regla gatilla RECHAZADO → **RECHAZADO**.
2. Si ninguna RECHAZADO y ≥1 PENDIENTE → **PENDIENTE**.
3. Si ninguna RECHAZADO ni PENDIENTE y ≥1 APROBADO → **APROBADO**.
4. Por defecto (ninguna regla aplica) → **PENDIENTE**, sin alertas.

## Formato de resultado
```json
{ "gasto_id": "g_125", "status": "APROBADO", "alertas": [] }
{ "gasto_id": "g_123", "status": "PENDIENTE", "alertas": [ { "codigo": "LIMITE_ANTIGUEDAD", "mensaje": "Gasto excede los 30 días. Requiere revisión." } ] }
{ "gasto_id": "g_124", "status": "RECHAZADO", "alertas": [ { "codigo": "POLITICA_CENTRO_COSTO", "mensaje": "El C.C. 'core_engineering' no puede reportar 'food'." } ] }
```

## Entregable más importante: tests unitarios
Cubrir **exhaustivamente cada regla y cada estado** (APROBADO/PENDIENTE/RECHAZADO), incluyendo bordes (días=30, 31, 60, 61; monto exactamente en aprobado_hasta / pendiente_hasta) y combinaciones de prioridad.

## Notas de diseño (para escalar en vivo)
- Política configurable, NO hardcodear límites.
- Pensar reglas componibles: cada regla = unidad que devuelve una evaluación parcial `{status, alerta?}`; un resolvedor aplica la prioridad. Agregar reglas nuevas = agregar una unidad, sin tocar el resto.
- La conversión de moneda es una dependencia inyectada (interfaz `ExchangeRateProvider`), con un mock para esta parte.
