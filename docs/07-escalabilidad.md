# 07 — Escalabilidad: ejes de crecimiento y puntos de extensión

> **Nota de alcance.** Este documento es **trabajo extra, por iniciativa propia** — no
> formaba parte del enunciado del desafío. Lo agregamos porque la entrevista en vivo
> *evolucionará* el código, y queríamos dejar mapeado dónde y cómo escala. Ver
> [`08-extras-iniciativa.md`](08-extras-iniciativa.md) para el catálogo completo de extras.

El diseño actual (Clean Architecture / Hexagonal) ya deja el dominio puro y aislado de la
infraestructura. Eso hace que la mayoría de los ejes de escala se resuelvan **agregando
adaptadores o reglas, sin tocar el núcleo**. Acá mapeamos cada eje a su punto real en el
código y al seam (costura) que lo habilita.

## Ejes de escala

### 1. Más reglas / reglas más complejas
- **Hoy:** patrón Strategy en `domain/rules/`, registro en `registry.py`, resolvedor de
  prioridades en `resolver.py`. Agregar una regla no toca motor ni resolvedor (Open/Closed).
- **Presión:** reglas con prioridad/severidad, reglas que dependen de otras, y
  **trazabilidad** (hoy `PartialEvaluation.rule` existe pero el resultado solo expone las
  alertas, no qué regla ganó).
- **Seam:** scaffold `_template.py` + skill `nueva-regla`. Para trazabilidad ver §7.

### 2. Más proveedores de tasas / resiliencia
- **Hoy:** puerto `ExchangeRateProvider` (`application/ports.py`); dos implementaciones
  (`MockExchangeRateProvider`, `OpenExchangeRatesClient`). Cache por fecha (resuelve N+1).
- **Presión:** el proveedor falla (red, rate limit), o se quiere un segundo proveedor de
  respaldo; cache que sobreviva entre corridas.
- **Seam:** un **provider decorador** (fallback/retry) que implementa el mismo puerto y
  envuelve a otro. Implementado como extra (ver `infrastructure/exchange_rates/`). Cache
  persistente quedaría como otro adaptador del puerto.

### 3. Volumen (CSV gigante / lote enorme)
- **Hoy:** `csv/reader.py` carga todo en memoria; `batch_analyzer.analyze` es secuencial.
  El N+1 ya está resuelto (1 llamada HTTP por fecha única).
- **Presión:** millones de filas no caben en memoria; el procesamiento serial es lento.
- **Seam:** lectura **streaming** (generador) para no materializar todo el CSV; la
  normalización es paralelizable por fecha. Streaming implementado como extra.

### 4. Múltiples políticas / versionado / multi-tenant
- **Hoy:** una `policy.json`, cargada en el CLI.
- **Presión:** varias empresas (multi-tenant), o una política que **cambia en el tiempo**
  (un gasto debe evaluarse contra la política vigente **a su fecha**).
- **Seam (diseñado, no implementado):** un `PolicyProvider` (puerto) que, dada una fecha
  y/o un tenant, devuelve la `Policy` aplicable. El motor ya recibe la `Policy` por
  parámetro, así que el cambio es de carga, no de dominio. **No lo forzamos** para no
  inflar el prototipo antes de la entrevista (ver nota de criterio abajo).

### 5. Exponerlo como servicio (API)
- **Hoy:** solo CLI (`cli/analyze.py`).
- **Presión:** consumir el motor desde otros sistemas (web, colas, webhooks).
- **Seam:** la capa `application` (`analyze`) se reusa **tal cual** detrás de un endpoint.
  Scaffold FastAPI agregado como extra (`api/`) — el dominio no se toca. Es la mejor
  demostración de que la arquitectura hexagonal paga.

### 6. Más anomalías / detección estadística
- **Hoy:** `application/anomalies.py` son funciones sueltas (duplicados, negativos)
  llamadas directo desde el analizador.
- **Presión:** outliers por empleado/categoría, umbrales configurables, más tipos.
- **Seam:** un **registry de detectores** espejo del de reglas. Skill `nueva-anomalia`.

### 7. Auditabilidad / observabilidad / i18n (diseñado)
- **Hoy:** mensajes de alerta en español hardcodeado; sin log estructurado ni audit trail.
- **Presión:** "¿por qué se rechazó este gasto?" debe ser trazable; mensajes multi-idioma.
- **Seam (diseñado):** el resultado podría exponer las reglas que dispararon. **Cuidado:**
  el enunciado fija el contrato de salida (`{gasto_id, status, alertas}`), así que
  cualquier traza debe ser **aditiva y opt-in** para no romperlo. i18n: catálogo de
  mensajes por `code` en vez de strings literales en cada regla.

## Resumen: estado de cada seam

| Eje | Seam | Estado |
|-----|------|--------|
| 1. Reglas | scaffold + registry | ✅ implementado + skill `nueva-regla` |
| 2. Tasas | provider con fallback/retry | ✅ implementado (extra) |
| 3. Volumen | reader streaming | ✅ implementado (extra) |
| 4. Políticas | `PolicyProvider` fechado | 📐 diseñado (no implementado: YAGNI pre-entrevista) |
| 5. API | endpoint sobre `application` | ✅ scaffold (extra) |
| 6. Anomalías | registry de detectores | 🛠️ skill `nueva-anomalia` |
| 7. Auditoría/i18n | traza aditiva + catálogo de mensajes | 📐 diseñado (no rompe el contrato del enunciado) |

## Nota de criterio (por qué no implementamos *todo*)
La entrevista busca **vernos evolucionar el código en vivo**. Pavimentar de más quitaría
gracia al ejercicio y oler­ía a over-engineering. Por eso distinguimos entre seams
**implementados** (aditivos, sin riesgo para el contrato del enunciado) y seams
**diseñados** (documentados acá, listos para construir cuando se pidan). Todo lo extra está
catalogado en [`08-extras-iniciativa.md`](08-extras-iniciativa.md).
