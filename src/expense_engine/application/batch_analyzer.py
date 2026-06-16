"""Analizador de lotes: ensambla Partes 1 y 2 sobre un conjunto de gastos.

Normaliza (convierte monedas) → valida (motor de reglas) → agrega resultados y
detecta anomalías.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from expense_engine.application.anomalies import (
    DuplicateGroup,
    find_exact_duplicates,
    find_negative_amounts,
)
from expense_engine.application.normalizer import normalize
from expense_engine.application.ports import ExchangeRateProvider
from expense_engine.domain.engine import validate_expense
from expense_engine.domain.models import (
    Expense,
    ExpenseRecord,
    Policy,
    Status,
    ValidationResult,
)
from expense_engine.domain.rules.base import EvaluationContext


@dataclass(frozen=True)
class BatchReport:
    """Resultado del análisis del lote."""

    results: list[ValidationResult]
    status_counts: dict[Status, int]
    duplicates: list[DuplicateGroup]
    negatives: list[Expense]


def analyze(
    records: Sequence[ExpenseRecord],
    policy: Policy,
    provider: ExchangeRateProvider,
    reference_date: date,
) -> BatchReport:
    """Procesa el lote completo y devuelve resultados agregados + anomalías."""
    normalized = normalize(records, provider)

    results: list[ValidationResult] = []
    for record in normalized:
        ctx = EvaluationContext(
            normalized_expense=record.normalized_expense,
            employee=record.employee,
            policy=policy,
            reference_date=reference_date,
        )
        results.append(validate_expense(ctx))

    status_counts: dict[Status, int] = {"APROBADO": 0, "PENDIENTE": 0, "RECHAZADO": 0}
    for result in results:
        status_counts[result.status] += 1

    expenses = [record.expense for record in records]
    return BatchReport(
        results=results,
        status_counts=status_counts,
        duplicates=find_exact_duplicates(expenses),
        negatives=find_negative_amounts(expenses),
    )
