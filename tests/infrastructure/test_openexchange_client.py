"""Tests del cliente de Open Exchange Rates (HTTP mockeado, sin red real)."""

from __future__ import annotations

from decimal import Decimal

import pytest
import responses

from expense_engine.application.ports import ExchangeRateProvider
from expense_engine.infrastructure.exchange_rates.openexchange_client import (
    ExchangeRateAPIError,
    OpenExchangeRatesClient,
    RateUnavailableError,
)

_HISTORICAL_URL = "https://openexchangerates.org/api/historical/2026-05-17.json"


def test_satisfies_provider_protocol() -> None:
    assert isinstance(OpenExchangeRatesClient(app_id="x"), ExchangeRateProvider)


@responses.activate
def test_converts_using_historical_rate() -> None:
    responses.add(
        responses.GET,
        _HISTORICAL_URL,
        json={"base": "USD", "rates": {"CLP": 950.0, "EUR": 0.92}},
        status=200,
    )
    client = OpenExchangeRatesClient(app_id="x")
    result = client.convert(Decimal("81000"), "CLP", "2026-05-17")
    assert result == Decimal("81000") / Decimal("950.0")


@responses.activate
def test_base_currency_makes_no_request() -> None:
    client = OpenExchangeRatesClient(app_id="x")
    assert client.convert(Decimal("50"), "USD", "2026-05-17") == Decimal("50")
    assert len(responses.calls) == 0


@responses.activate
def test_caches_rates_per_date() -> None:
    """Pedir la misma fecha dos veces hace UNA sola llamada HTTP (anti N+1)."""
    responses.add(
        responses.GET,
        _HISTORICAL_URL,
        json={"base": "USD", "rates": {"CLP": 950.0}},
        status=200,
    )
    client = OpenExchangeRatesClient(app_id="x")
    client.convert(Decimal("100"), "CLP", "2026-05-17")
    client.convert(Decimal("200"), "CLP", "2026-05-17")
    assert len(responses.calls) == 1


@responses.activate
def test_non_200_raises_api_error() -> None:
    responses.add(responses.GET, _HISTORICAL_URL, json={"error": True}, status=401)
    client = OpenExchangeRatesClient(app_id="x")
    with pytest.raises(ExchangeRateAPIError):
        client.convert(Decimal("1"), "CLP", "2026-05-17")


@responses.activate
def test_missing_currency_raises() -> None:
    responses.add(
        responses.GET,
        _HISTORICAL_URL,
        json={"base": "USD", "rates": {"EUR": 0.92}},
        status=200,
    )
    client = OpenExchangeRatesClient(app_id="x")
    with pytest.raises(RateUnavailableError):
        client.convert(Decimal("1"), "CLP", "2026-05-17")
