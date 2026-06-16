"""Tests de la Regla 1 — Antigüedad."""

from __future__ import annotations

from datetime import timedelta

import pytest

from expense_engine.domain.models import Status
from expense_engine.domain.rules.age import AgeRule
from expense_engine.domain.rules.base import EvaluationContext
from tests.helpers import REFERENCE_DATE, build_context


def _context_aged(days: int) -> EvaluationContext:
    """Contexto cuyo gasto tiene exactamente `days` días de antigüedad."""
    expense_date = (REFERENCE_DATE - timedelta(days=days)).isoformat()
    # Categoría sin límite para aislar la regla de antigüedad.
    return build_context(category="software", expense_date=expense_date)


@pytest.mark.parametrize(
    "days, expected",
    [
        (0, "APROBADO"),
        (1, "APROBADO"),
        (30, "APROBADO"),  # borde superior de APROBADO
        (31, "PENDIENTE"),  # borde inferior de PENDIENTE
        (45, "PENDIENTE"),
        (60, "PENDIENTE"),  # borde superior de PENDIENTE
        (61, "RECHAZADO"),  # borde inferior de RECHAZADO
        (200, "RECHAZADO"),
    ],
)
def test_age_boundaries(days: int, expected: Status) -> None:
    result = AgeRule().evaluate(_context_aged(days))
    assert result is not None
    assert result.status == expected


def test_approved_has_no_alert() -> None:
    result = AgeRule().evaluate(_context_aged(10))
    assert result is not None
    assert result.alert is None


def test_pending_has_alert() -> None:
    result = AgeRule().evaluate(_context_aged(45))
    assert result is not None
    assert result.alert is not None
    assert result.alert.code == "LIMITE_ANTIGUEDAD"


def test_rejected_has_alert() -> None:
    result = AgeRule().evaluate(_context_aged(100))
    assert result is not None
    assert result.alert is not None
    assert result.alert.code == "LIMITE_ANTIGUEDAD"
