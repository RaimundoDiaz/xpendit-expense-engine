"""Regla 1 — Antigüedad del gasto."""

from __future__ import annotations

from datetime import date

from expense_engine.domain.models import Alert
from expense_engine.domain.rules.base import EvaluationContext, PartialEvaluation


class AgeRule:
    """Evalúa la antigüedad del gasto contra los umbrales de la política.

    - 0 ≤ días ≤ pendiente_dias            → APROBADO
    - pendiente_dias < días ≤ rechazado_dias → PENDIENTE
    - días > rechazado_dias                → RECHAZADO

    Siempre aplica (todo gasto tiene una antigüedad).
    """

    name = "LIMITE_ANTIGUEDAD"

    def evaluate(self, ctx: EvaluationContext) -> PartialEvaluation | None:
        expense_date = date.fromisoformat(ctx.normalized_expense.expense.date)
        days = (ctx.reference_date - expense_date).days
        limit = ctx.policy.age_limit

        if days <= limit.pending_days:
            return PartialEvaluation(status="APROBADO", rule=self.name)

        if days <= limit.rejected_days:
            return PartialEvaluation(
                status="PENDIENTE",
                rule=self.name,
                alert=Alert(
                    code=self.name,
                    message=f"Gasto excede los {limit.pending_days} días. Requiere revisión.",
                ),
            )

        return PartialEvaluation(
            status="RECHAZADO",
            rule=self.name,
            alert=Alert(
                code=self.name,
                message=f"Gasto excede los {limit.rejected_days} días. Rechazado por antigüedad.",
            ),
        )
