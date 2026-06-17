"""Provider de tasas con fallback — implementa `ExchangeRateProvider` envolviendo a otros.

Resiliencia (eje de escala §2 en docs/07-escalabilidad.md): encadena varios providers e
intenta cada uno en orden, devolviendo la primera conversión exitosa. Si todos fallan,
propaga el último error. Ejemplo de uso: `[cliente_real, cache_local, mock_de_respaldo]`.

Como cumple el mismo puerto, es transparente para el resto del sistema (normalizer, CLI, API).
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from expense_engine.application.ports import ExchangeRateProvider


class AllProvidersFailedError(RuntimeError):
    """Ningún provider de la cadena pudo convertir el monto."""


class FallbackExchangeRateProvider:
    """Usa el primer provider de la cadena que responda sin lanzar una excepción."""

    def __init__(self, providers: Sequence[ExchangeRateProvider]) -> None:
        if not providers:
            raise ValueError("Se requiere al menos un provider para el fallback.")
        self._providers = tuple(providers)

    def convert(self, amount: Decimal, currency: str, date: str) -> Decimal:
        last_error: Exception | None = None
        for provider in self._providers:
            try:
                return provider.convert(amount, currency, date)
            except Exception as exc:  # noqa: BLE001 — a propósito: se reintenta con el siguiente
                last_error = exc
        raise AllProvidersFailedError(
            f"Todos los providers fallaron al convertir '{currency}' en {date}."
        ) from last_error
