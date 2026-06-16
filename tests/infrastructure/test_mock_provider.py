"""Tests del proveedor de tasas mock (in-memory, sin red)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from expense_engine.application.ports import ExchangeRateProvider
from expense_engine.infrastructure.exchange_rates.mock_provider import MockExchangeRateProvider


def test_satisfies_provider_protocol() -> None:
    assert isinstance(MockExchangeRateProvider(), ExchangeRateProvider)


def test_base_currency_unchanged() -> None:
    provider = MockExchangeRateProvider({"CLP": Decimal("950")})
    assert provider.convert(Decimal("100"), "USD", "2026-06-01") == Decimal("100")


def test_converts_other_currency() -> None:
    # 9500 CLP a 950 CLP/USD = 10 USD
    provider = MockExchangeRateProvider({"CLP": Decimal("950")})
    assert provider.convert(Decimal("9500"), "CLP", "2026-06-01") == Decimal("10")


def test_unknown_currency_raises() -> None:
    provider = MockExchangeRateProvider({})
    with pytest.raises(KeyError):
        provider.convert(Decimal("1"), "EUR", "2026-06-01")
