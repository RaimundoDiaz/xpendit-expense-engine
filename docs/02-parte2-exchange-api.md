# 02 — Parte 2: Cliente de Tasas de Cambio (Integración I/O)

Reemplazar el mock de la Parte 1 con integración real a **Open Exchange Rates**.

## Pre-requisito / credencial
- Cuenta gratuita en Open Exchange Rates; obtener el `app_id` (API Key) del Dashboard.
- **Ya tenemos la key**: está en `.env.local` como `open_exchange_app_id=...` (gitignored, NO commitear). Cargar con `python-dotenv` o `os.environ`. Proveer un `.env.example` con el nombre de la variable sin el valor.

## Diseño clave
El cliente API debe implementar la **misma interfaz** que el mock inyectado en Parte 1 (ej. un `ProveedorTasas`/protocolo con `convertir(monto, moneda, fecha) -> float` o `obtener_tasa(moneda, fecha)`). El motor de reglas no cambia — solo se inyecta el cliente real en vez del mock. Demuestra separación de responsabilidades. En Python esto se modela bien con `typing.Protocol` o una ABC.

## API Open Exchange Rates (verificado en docs oficiales, 16 jun 2026)
- Tasas actuales: `GET /latest.json?app_id=APP_ID`
- **Tasas históricas por fecha**: `GET /historical/YYYY-MM-DD.json?app_id=APP_ID` (datos desde 1 ene 1999).
- **Plan Forever Free**: incluye datos históricos, base **USD fija**, 1.000 requests/mes. La limitación de "solo base USD" NO nos afecta porque nuestra moneda_base es USD.
- `rates[moneda]` = unidades de esa moneda por 1 USD → `monto_en_USD = monto / rates[moneda]`. Para USD la tasa es 1.

## DECISIÓN: usar la tasa histórica del DÍA DEL GASTO (no la de hoy)
Razones: (1) correcto en el dominio — un gasto se valoriza a la tasa de su fecha, comportamiento contable esperado en expense management; (2) CLP/MXN se mueven 5-15% en el rango del CSV (dic-2025 a jun-2026) → gastos cerca de un umbral (100/150 USD food) pueden cambiar de veredicto; (3) es lo que da sentido al bonus N+1 — con una sola tasa "today" habría 1 request y no habría nada que optimizar. El enunciado describe el bonus como "una llamada por fecha única", lo que confirma que esperan histórico-por-fecha.
OJO: no confundir `fecha_referencia` ("hoy", para antigüedad) con `gasto.fecha` (para la tasa). Son independientes.

## Manejo de errores (criterio de evaluación)
Timeouts, status != 200, moneda no soportada, rate limits. Fallar de forma controlada (errores tipados, no crashear el lote completo).

Ver `01-parte1-rules-engine.md` (interfaz a respetar) y `03-parte3-batch-analyzer.md` (optimización N+1 sobre estas llamadas).
