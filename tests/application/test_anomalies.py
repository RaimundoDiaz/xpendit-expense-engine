"""Tests de la detección de anomalías."""

from __future__ import annotations

from decimal import Decimal

from expense_engine.application.anomalies import find_exact_duplicates, find_negative_amounts
from expense_engine.domain.models import Expense


def _expense(expense_id: str, amount: str, currency: str = "USD", date: str = "2026-06-06") -> Expense:
    return Expense(
        id=expense_id, amount=Decimal(amount), currency=currency, date=date, category="food"
    )


def test_finds_exact_duplicate_group() -> None:
    expenses = [
        _expense("g_042", "90"),
        _expense("g_043", "90"),
        _expense("g_044", "90"),
        _expense("g_045", "100"),  # distinto monto → no duplicado
    ]
    groups = find_exact_duplicates(expenses)
    assert len(groups) == 1
    assert groups[0].expense_ids == ["g_042", "g_043", "g_044"]
    assert groups[0].amount == Decimal("90")


def test_no_duplicates_when_dates_differ() -> None:
    expenses = [
        _expense("g_1", "90", date="2026-06-06"),
        _expense("g_2", "90", date="2026-06-07"),
    ]
    assert find_exact_duplicates(expenses) == []


def test_finds_negative_amounts() -> None:
    expenses = [_expense("g_1", "50"), _expense("g_2", "-30"), _expense("g_3", "-1")]
    negatives = find_negative_amounts(expenses)
    assert [e.id for e in negatives] == ["g_2", "g_3"]


def test_no_negatives_returns_empty() -> None:
    expenses = [_expense("g_1", "50"), _expense("g_2", "100")]
    assert find_negative_amounts(expenses) == []
