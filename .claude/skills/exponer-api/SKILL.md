---
name: exponer-api
description: Expone el motor de gastos de Xpendit como API HTTP (FastAPI) reusando la capa application sin tocar el dominio. Úsala cuando el usuario pida "exponer una API", "endpoint HTTP", "servicio web", "validar gastos por REST", o "montar FastAPI sobre el motor".
---

# Exponer el motor como API HTTP

La gracia de la arquitectura hexagonal: una API es **otro adaptador de entrada**, igual que el
CLI. Reusa la capa `application` (`batch_analyzer.analyze`, `engine.validate_expense`) **sin
tocar el dominio**. Esto demuestra el eje §5 de `docs/07-escalabilidad.md`.

## 1. Definir el alcance
- **Endpoints:** lo mínimo útil suele ser:
  - `POST /validate` — valida **un** gasto (cuerpo: gasto + empleado) → `ValidationResult`.
  - `POST /analyze` — valida un **lote** → `BatchReport` (conteos + anomalías).
- **Provider de tasas:** ¿API real (`OpenExchangeRatesClient`, requiere API key) o mock
  inyectable para demo/tests? Hazlo **inyectable** (dependencia de FastAPI) para poder testear
  sin red.
- **Fecha de referencia:** parámetro opcional; default `date.today()` (igual que el CLI).

## 2. Crear el paquete `api/`
- `src/expense_engine/api/__init__.py` y `src/expense_engine/api/app.py` con la app FastAPI.
- Modelos de request en español (mismos alias que el dominio) — puedes reusar `Expense` /
  `Employee` de `domain/models.py`, que ya parsean alias en español vía Pydantic.
- La respuesta: `result.model_dump(by_alias=True)` para conservar el contrato
  `{gasto_id, status, alertas}` del enunciado.
- Inyecta el `ExchangeRateProvider` con `Depends(...)` para poder sobreescribirlo en tests.

## 3. Dependencias (opcional, aislada)
- Agrega `fastapi` y `httpx` (para el TestClient) a un archivo **separado**
  `requirements-api.txt` o a un extra en `pyproject.toml` (`[project.optional-dependencies]`),
  **no** a `requirements.txt`. La API es un extra: las Partes 1–3 no deben requerirla.

## 4. Tests
- En `tests/api/test_app.py` con `fastapi.testclient.TestClient`.
- Sobreescribe la dependencia del provider por un `MockExchangeRateProvider` (sin red).
- Cubre: validación OK (200 + status correcto), gasto malformado (422 de Pydantic), lote.

## 5. Documentar como extra
La API es **iniciativa propia**, no parte del desafío. Asegúrate de que quede listada en
`docs/08-extras-iniciativa.md` (y que sus deps sean opcionales). Menciona cómo levantarla:
`uvicorn expense_engine.api.app:app --reload`.

## 6. Verificar
`python -m pytest -q` y `pyright`. Reporta el resultado.

## Referencias del repo
- Casos de uso a reusar: `application/batch_analyzer.py` (`analyze`), `domain/engine.py` (`validate_expense`)
- Puerto de tasas: `application/ports.py` (`ExchangeRateProvider`) — inyéctalo
- Contrato de salida: `domain/models.py` (`ValidationResult`, serializa `{gasto_id, status, alertas}`)
- Adaptador equivalente ya existente: `cli/analyze.py` (mismo ensamblaje, otra entrada)
