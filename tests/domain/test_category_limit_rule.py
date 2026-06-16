"""Tests de la Regla 2 — Límite de monto por categoría."""

from __future__ import annotations

import pytest

from expense_engine.domain.models import Status
from expense_engine.domain.rules.category_limit import CategoryLimitRule
from tests.helpers import build_context


@pytest.mark.parametrize(
    "amount, expected",
    [
        ("50", "APROBADO"),
        ("100", "APROBADO"),  # borde: aprobado_hasta
        ("100.01", "PENDIENTE"),  # apenas sobre el límite aprobado
        ("150", "PENDIENTE"),  # borde: pendiente_hasta
        ("150.01", "RECHAZADO"),  # apenas sobre el límite pendiente
        ("500", "RECHAZADO"),
    ],
)
def test_food_limits(amount: str, expected: Status) -> None:
    result = CategoryLimitRule().evaluate(build_context(category="food", amount_base=amount))
    assert result is not None
    assert result.status == expected


@pytest.mark.parametrize(
    "amount, expected",
    [
        ("200", "APROBADO"),  # transport: aprobado==pendiente==200 → sin banda PENDIENTE
        ("200.01", "RECHAZADO"),
    ],
)
def test_transport_limits(amount: str, expected: Status) -> None:
    result = CategoryLimitRule().evaluate(
        build_context(category="transport", amount_base=amount)
    )
    assert result is not None
    assert result.status == expected


def test_category_without_limit_returns_none() -> None:
    # "software" no tiene límite definido en la política → la regla no aplica.
    result = CategoryLimitRule().evaluate(build_context(category="software", amount_base="9999"))
    assert result is None


def test_pending_has_alert() -> None:
    result = CategoryLimitRule().evaluate(build_context(category="food", amount_base="120"))
    assert result is not None
    assert result.alert is not None
    assert result.alert.code == "LIMITE_CATEGORIA"
