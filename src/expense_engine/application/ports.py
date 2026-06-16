"""Puertos (interfaces) que la infraestructura implementa.

Definidos en la capa de aplicación; el dominio y la aplicación dependen de estas
abstracciones, no de implementaciones concretas (inversión de dependencias).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol, runtime_checkable


@runtime_checkable
class ExchangeRateProvider(Protocol):
    """Convierte un monto a la moneda base. El mock y el cliente real lo implementan."""

    def convert(self, amount: Decimal, currency: str, date: str) -> Decimal:
        """Devuelve `amount` (en `currency`, con fecha `date`) convertido a la moneda base."""
        ...
