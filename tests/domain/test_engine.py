"""Tests del motor (end-to-end del dominio) con casos reales del CSV.

Estos casos fueron trazados a mano contra el enunciado:
  - g_001: food 50 USD, 15 días, sales_team            → APROBADO
  - g_002: food 120 USD, ~20 días, sales_team          → PENDIENTE (excede límite aprobado)
  - g_011: food 50 USD, 15 días, core_engineering      → RECHAZADO (regla cruzada)
  - g_023: lodging 50 USD, ~167 días, finance          → RECHAZADO (antigüedad)
"""

from __future__ import annotations

from expense_engine.domain.engine import validate_expense
from tests.helpers import build_context


def test_g001_approved() -> None:
    ctx = build_context(
        expense_id="g_001",
        category="food",
        amount_base="50",
        expense_date="2026-06-01",
        cost_center="sales_team",
    )
    result = validate_expense(ctx)
    assert result.status == "APROBADO"
    assert result.alerts == []


def test_g002_pending_by_category_limit() -> None:
    ctx = build_context(
        expense_id="g_002",
        category="food",
        amount_base="120",
        expense_date="2026-05-27",
        cost_center="sales_team",
    )
    result = validate_expense(ctx)
    assert result.status == "PENDIENTE"
    assert [a.code for a in result.alerts] == ["LIMITE_CATEGORIA"]


def test_g011_rejected_by_cost_center_rule() -> None:
    ctx = build_context(
        expense_id="g_011",
        category="food",
        amount_base="50",
        expense_date="2026-06-01",
        cost_center="core_engineering",
    )
    result = validate_expense(ctx)
    assert result.status == "RECHAZADO"
    assert [a.code for a in result.alerts] == ["POLITICA_CENTRO_COSTO"]


def test_g023_rejected_by_age() -> None:
    ctx = build_context(
        expense_id="g_023",
        category="lodging",
        amount_base="50",
        expense_date="2025-12-31",
        cost_center="finance",
    )
    result = validate_expense(ctx)
    assert result.status == "RECHAZADO"
    assert [a.code for a in result.alerts] == ["LIMITE_ANTIGUEDAD"]


def test_result_serializes_with_spec_keys() -> None:
    """El output debe usar exactamente las llaves del enunciado."""
    ctx = build_context(
        expense_id="g_011",
        category="food",
        amount_base="50",
        expense_date="2026-06-01",
        cost_center="core_engineering",
    )
    dumped = validate_expense(ctx).model_dump(by_alias=True)
    assert dumped == {
        "gasto_id": "g_011",
        "status": "RECHAZADO",
        "alertas": [
            {
                "codigo": "POLITICA_CENTRO_COSTO",
                "mensaje": "El C.C. 'core_engineering' no puede reportar 'food'.",
            }
        ],
    }
