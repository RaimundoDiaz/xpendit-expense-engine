"""Tests del provider de tasas con fallback (extra — eje de escala §2)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from expense_engine.infrastructure.exchange_rates.fallback_provider import (
    AllProvidersFailedError,
    FallbackExchangeRateProvider,
)


class _Stub:
    """Provider de prueba: devuelve un valor fijo o lanza si `fail=True`."""

    def __init__(self, value: str = "0", fail: bool = False) -> None:
        self._value = Decimal(value)
        self._fail = fail
        self.calls = 0

    def convert(self, amount: Decimal, currency: str, date: str) -> Decimal:
        self.calls += 1
        if self._fail:
            raise RuntimeError("provider caído")
        return self._value


def test_uses_first_provider_and_skips_the_rest() -> None:
    first, second = _Stub(value="10"), _Stub(value="20")
    provider = FallbackExchangeRateProvider([first, second])

    assert provider.convert(Decimal("1"), "EUR", "2026-06-01") == Decimal("10")
    assert first.calls == 1
    assert second.calls == 0  # no se llama si el primero responde


def test_falls_back_to_next_when_one_fails() -> None:
    failing, working = _Stub(fail=True), _Stub(value="33")
    provider = FallbackExchangeRateProvider([failing, working])

    assert provider.convert(Decimal("1"), "EUR", "2026-06-01") == Decimal("33")
    assert failing.calls == 1
    assert working.calls == 1


def test_raises_when_all_providers_fail() -> None:
    provider = FallbackExchangeRateProvider([_Stub(fail=True), _Stub(fail=True)])
    with pytest.raises(AllProvidersFailedError):
        provider.convert(Decimal("1"), "EUR", "2026-06-01")


def test_requires_at_least_one_provider() -> None:
    with pytest.raises(ValueError):
        FallbackExchangeRateProvider([])
