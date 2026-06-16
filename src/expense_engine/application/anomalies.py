"""Detección de anomalías en un lote de gastos.

Implementa las 2 anomalías del enunciado:
  - Duplicados exactos: gastos con mismo monto, moneda y fecha.
  - Montos negativos: gastos con montos erróneos (< 0).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from expense_engine.domain.models import Expense


@dataclass(frozen=True)
class DuplicateGroup:
    """Un grupo de gastos con (monto, moneda, fecha) idénticos."""

    amount: Decimal
    currency: str
    date: str
    expense_ids: list[str]


def find_exact_duplicates(expenses: Sequence[Expense]) -> list[DuplicateGroup]:
    """Agrupa por (monto, moneda, fecha) y devuelve los grupos con más de un gasto.

    Criterio literal del enunciado: monto + moneda + fecha. No incluye el empleado;
    el análisis comenta aparte los casos del mismo empleado (señal más fuerte de
    doble rendición).
    """
    groups: dict[tuple[Decimal, str, str], list[str]] = {}
    for expense in expenses:
        key = (expense.amount, expense.currency, expense.date)
        groups.setdefault(key, []).append(expense.id)

    return [
        DuplicateGroup(amount=amount, currency=currency, date=date, expense_ids=ids)
        for (amount, currency, date), ids in groups.items()
        if len(ids) > 1
    ]


def find_negative_amounts(expenses: Sequence[Expense]) -> list[Expense]:
    """Devuelve los gastos con monto negativo."""
    return [expense for expense in expenses if expense.amount < 0]
