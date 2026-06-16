"""Cliente real de Open Exchange Rates — implementa el puerto `ExchangeRateProvider`.

Usa el endpoint histórico (`/historical/YYYY-MM-DD.json`) para convertir cada gasto
con la tasa del día en que se realizó. Cachea las tasas por fecha en memoria, de modo
que pedir la misma fecha varias veces hace una sola llamada HTTP (evita el problema N+1).

El plan gratuito de Open Exchange Rates usa base USD; `rates[moneda]` son las unidades
de esa moneda por 1 USD, por lo que `monto_USD = monto / rates[moneda]`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import requests


class ExchangeRateError(RuntimeError):
    """Error base del cliente de tasas de cambio."""


class ExchangeRateAPIError(ExchangeRateError):
    """Falla al contactar la API o respuesta inválida (red, timeout, status != 200)."""


class RateUnavailableError(ExchangeRateError):
    """La moneda pedida no está disponible en la respuesta de la API."""


class OpenExchangeRatesClient:
    """Proveedor de tasas respaldado por la API de Open Exchange Rates."""

    BASE_URL = "https://openexchangerates.org/api"

    def __init__(
        self,
        app_id: str,
        base: str = "USD",
        timeout: float = 10.0,
        session: requests.Session | None = None,
    ) -> None:
        self._app_id = app_id
        self._base = base
        self._timeout = timeout
        self._session = session if session is not None else requests.Session()
        # Cache: fecha -> { moneda: tasa }. La clave del N+1: una entrada por fecha única.
        self._cache: dict[str, dict[str, Decimal]] = {}

    def convert(self, amount: Decimal, currency: str, date: str) -> Decimal:
        """Convierte `amount` (en `currency`, fecha `date`) a la moneda base."""
        if currency == self._base:
            return amount
        rates = self._rates_for(date)
        if currency not in rates:
            raise RateUnavailableError(
                f"No hay tasa para '{currency}' en la fecha {date}."
            )
        return amount / rates[currency]

    def _rates_for(self, date: str) -> dict[str, Decimal]:
        """Devuelve las tasas de una fecha, usando cache (1 llamada HTTP por fecha)."""
        cached = self._cache.get(date)
        if cached is None:
            cached = self._fetch(date)
            self._cache[date] = cached
        return cached

    def _fetch(self, date: str) -> dict[str, Decimal]:
        url = f"{self.BASE_URL}/historical/{date}.json"
        try:
            response = self._session.get(
                url, params={"app_id": self._app_id}, timeout=self._timeout
            )
        except requests.RequestException as exc:
            raise ExchangeRateAPIError(f"Error de red al pedir tasas de {date}: {exc}") from exc

        if response.status_code != 200:
            raise ExchangeRateAPIError(
                f"La API respondió {response.status_code} para la fecha {date}."
            )

        payload: object = response.json()
        if not isinstance(payload, dict):
            raise ExchangeRateAPIError(f"Respuesta inesperada de la API para {date}.")

        raw_rates = cast(dict[str, object], payload).get("rates")
        if not isinstance(raw_rates, dict):
            raise ExchangeRateAPIError(f"La respuesta no incluye 'rates' para {date}.")

        rates: dict[str, Decimal] = {}
        for currency, rate in cast(dict[str, object], raw_rates).items():
            rates[currency] = Decimal(str(rate))
        return rates
