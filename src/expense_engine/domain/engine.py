"""El motor de validación: lógica pura, sin red ni archivos.

Recolecta la opinión de cada regla y delega en el resolvedor la decisión final.
El motor no conoce monedas ni tasas de cambio: recibe el gasto con su monto ya
convertido a la moneda base (ver `NormalizedExpense`).
"""

from __future__ import annotations

from collections.abc import Sequence

from expense_engine.domain.models import ValidationResult
from expense_engine.domain.resolver import resolve
from expense_engine.domain.rules.base import EvaluationContext, PartialEvaluation, Rule
from expense_engine.domain.rules.registry import DEFAULT_RULES


def validate_expense(
    ctx: EvaluationContext,
    rules: Sequence[Rule] = DEFAULT_RULES,
) -> ValidationResult:
    """Valida un gasto aplicando todas las reglas y resolviendo el estado final."""
    evaluations: list[PartialEvaluation] = []
    for rule in rules:
        evaluation = rule.evaluate(ctx)
        if evaluation is not None:
            evaluations.append(evaluation)

    return resolve(ctx.normalized_expense.expense.id, evaluations)
