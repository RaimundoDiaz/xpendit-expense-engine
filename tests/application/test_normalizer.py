"""Tests del normalizador (conversión de montos a la moneda base)."""

from __future__ import annotations

from decimal import Decimal

from expense_engine.application.normalizer import normalize
from expense_engine.domain.models import Employee, Expense, ExpenseRecord
from expense_engine.infrastructure.exchange_rates.mock_provider import MockExchangeRateProvider


def _record(expense_id: str, amount: str, currency: str) -> ExpenseRecord:
    expense = Expense(
        id=expense_id, amount=Decimal(amount), currency=currency, date="2026-05-17", category="food"
    )
    employee = Employee(id="e_1", first_name="N", last_name="N", cost_center="sales_team")
    return ExpenseRecord(expense=expense, employee=employee)


def test_converts_each_record_to_base() -> None:
    provider = MockExchangeRateProvider({"CLP": Decimal("950")})
    records = [_record("g_1", "50", "USD"), _record("g_2", "9500", "CLP")]

    normalized = normalize(records, provider)

    assert normalized[0].normalized_expense.amount_base == Decimal("50")  # USD intacto
    assert normalized[1].normalized_expense.amount_base == Decimal("10")  # 9500/950
    # El gasto original se conserva
    assert normalized[1].normalized_expense.expense.amount == Decimal("9500")
    assert normalized[1].employee.id == "e_1"
