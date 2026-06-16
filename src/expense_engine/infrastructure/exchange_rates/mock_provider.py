"""Proveedor de tasas en memoria — para la Parte 1 y para los tests. Sin red.

Cumple el puerto `ExchangeRateProvider` con tasas fijas inyectadas, igual que el
cliente real: las tasas son "unidades de moneda por 1 unidad de la base" (convención
de Open Exchange Rates, base USD).
"""

from __future__ import annotations

from decimal import Decimal


class MockExchangeRateProvider:
    """Tasas fijas en memoria. `rates[moneda]` = unidades de esa moneda por 1 USD."""

    def __init__(self, rates: dict[str, Decimal] | None = None, base: str = "USD") -> None:
        self._rates: dict[str, Decimal] = dict(rates) if rates else {}
        self._base = base

    def convert(self, amount: Decimal, currency: str, date: str) -> Decimal:
        if currency == self._base:
            return amount
        if currency not in self._rates:
            raise KeyError(f"Tasa no disponible para la moneda '{currency}'")
        return amount / self._rates[currency]
