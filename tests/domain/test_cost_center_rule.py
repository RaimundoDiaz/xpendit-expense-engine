"""Tests de la Regla 3 — Regla cruzada de centro de costo."""

from __future__ import annotations

from expense_engine.domain.rules.cost_center import CostCenterRule
from tests.helpers import build_context


def test_prohibited_combination_is_rejected() -> None:
    # core_engineering + food está prohibido en la política de ejemplo.
    result = CostCenterRule().evaluate(
        build_context(cost_center="core_engineering", category="food")
    )
    assert result is not None
    assert result.status == "RECHAZADO"
    assert result.alert is not None
    assert result.alert.code == "POLITICA_CENTRO_COSTO"


def test_same_cost_center_other_category_is_allowed() -> None:
    result = CostCenterRule().evaluate(
        build_context(cost_center="core_engineering", category="software")
    )
    assert result is None


def test_other_cost_center_same_category_is_allowed() -> None:
    result = CostCenterRule().evaluate(
        build_context(cost_center="sales_team", category="food")
    )
    assert result is None
