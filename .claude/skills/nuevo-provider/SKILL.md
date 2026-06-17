---
name: nuevo-provider
description: Crea un proveedor de tasas de cambio nuevo para el motor de gastos de Xpendit — implementa el puerto ExchangeRateProvider (cliente real, mock, o decorador de fallback/retry) con su test. Úsala cuando el usuario pida "agregar un provider/proveedor de tasas", "soportar otra API de cambio", "fallback/retry para las tasas", o "cache persistente de tasas".
---

# Crear un proveedor de tasas de cambio nuevo

Las tasas son un puerto inyectable: `ExchangeRateProvider` en `application/ports.py`, con un
único método `convert(amount: Decimal, currency: str, date: str) -> Decimal`. El dominio y la
aplicación dependen del puerto, no de implementaciones concretas. Agregar un provider = crear
una clase que cumpla el puerto; nada del dominio cambia.

## 1. Reunir la especificación
Pregunta (si no está claro):
- **Tipo de provider:**
  - *Cliente real* contra una API (como `OpenExchangeRatesClient`).
  - *Mock* con tasas fijas (como `MockExchangeRateProvider`, para tests).
  - *Decorador* que envuelve a otro provider para agregar **fallback, retry o cache**
    (recibe uno o más providers en el constructor y delega en ellos).
- **Convención de tasas:** `rates[moneda]` = unidades de esa moneda por 1 de la base (USD),
  por lo que `monto_base = monto / rates[moneda]`. Mantenla consistente con los existentes.
- **Manejo de errores:** ¿qué pasa si la moneda no existe / la red falla? Reusa la jerarquía
  `ExchangeRateError` de `openexchange_client.py` cuando aplique.
- **Secretos:** si usa API key, cárgala vía `infrastructure/config.py` (nunca hardcodear).

## 2. Crear el archivo del provider
- Ubícalo en `src/expense_engine/infrastructure/exchange_rates/<nombre>.py`.
- La clase debe tener `convert(self, amount, currency, date) -> Decimal`. No necesita heredar
  de nada: el puerto es un `Protocol` (tipado estructural).
- Para un **decorador de fallback**: el constructor recibe `providers: Sequence[ExchangeRateProvider]`;
  `convert` intenta cada uno en orden y devuelve el primero que no lance, propagando el último error.
- Para **cache**: cachea por `date` (clave del N+1), igual que `OpenExchangeRatesClient._cache`.
- Mensajes y docstrings en español, mismo tono que los providers existentes.

## 3. Crear el test
- En `tests/infrastructure/test_<nombre>.py`.
- Para clientes HTTP: inyecta una `requests.Session` fake (ver `test_openexchange_client.py`).
- Para decoradores: inyecta providers de prueba (uno que falle, uno que responda) y verifica
  el orden de fallback, los reintentos y la propagación de errores.
- Cubre: conversión OK, moneda base (devuelve el monto sin tocar), moneda inexistente, fallo de red.

## 4. Conectar (si corresponde)
El CLI (`cli/analyze.py`) instancia `OpenExchangeRatesClient`. Si el provider nuevo debe usarse
ahí (p. ej. envolver el cliente real en el decorador de fallback), edita esa línea. Para un
provider solo-tests no hace falta tocar el CLI.

## 5. Verificar
`python -m pytest -q` y `pyright`. Reporta el resultado.

## Referencias del repo
- Puerto: `application/ports.py` (`ExchangeRateProvider`)
- Implementaciones: `infrastructure/exchange_rates/openexchange_client.py`, `mock_provider.py`
- Errores: `ExchangeRateError`, `ExchangeRateAPIError`, `RateUnavailableError`
- Uso: `application/normalizer.py`, `cli/analyze.py`
- Tests de referencia: `tests/infrastructure/test_openexchange_client.py`, `test_mock_provider.py`
