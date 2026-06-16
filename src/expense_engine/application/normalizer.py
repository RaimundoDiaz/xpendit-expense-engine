"""Normalización de gastos: convierte el monto de cada gasto a la moneda base.

Usa el puerto `ExchangeRateProvider`. La optimización N+1 vive en el proveedor:
`OpenExchangeRatesClient` cachea las tasas por fecha, así que aunque aquí llamemos
`convert` una vez por gasto, solo se hace UNA llamada HTTP por fecha única del lote.
"""

from __future__ import annotations

from collections.abc import Sequence

from expense_engine.application.ports import ExchangeRateProvider
from expense_engine.domain.models import ExpenseRecord, NormalizedExpense, NormalizedRecord


def normalize(
    records: Sequence[ExpenseRecord], provider: ExchangeRateProvider
) -> list[NormalizedRecord]:
    """Convierte el monto de cada registro a la moneda base."""
    normalized: list[NormalizedRecord] = []
    for record in records:
        expense = record.expense
        amount_base = provider.convert(expense.amount, expense.currency, expense.date)
        normalized.append(
            NormalizedRecord(
                normalized_expense=NormalizedExpense(
                    expense=expense, amount_base=amount_base
                ),
                employee=record.employee,
            )
        )
    return normalized
