"""Regla 2 — Límite de monto por categoría."""

from __future__ import annotations

from expense_engine.domain.models import Alert
from expense_engine.domain.rules.base import EvaluationContext, PartialEvaluation


class CategoryLimitRule:
    """Evalúa el monto (ya en moneda base) contra el límite de su categoría.

    - monto ≤ aprobado_hasta              → APROBADO
    - aprobado_hasta < monto ≤ pendiente  → PENDIENTE
    - monto > pendiente_hasta             → RECHAZADO

    Devuelve `None` si la categoría no tiene límite definido en la política.
    """

    name = "LIMITE_CATEGORIA"

    def evaluate(self, ctx: EvaluationContext) -> PartialEvaluation | None:
        expense = ctx.normalized_expense.expense
        limit = ctx.policy.category_limits.get(expense.category)
        if limit is None:
            return None

        amount = ctx.normalized_expense.amount_base

        if amount <= limit.approved_up_to:
            return PartialEvaluation(status="APROBADO", rule=self.name)

        if amount <= limit.pending_up_to:
            return PartialEvaluation(
                status="PENDIENTE",
                rule=self.name,
                alert=Alert(
                    code=self.name,
                    message=(
                        f"Gasto de '{expense.category}' excede el límite aprobado. "
                        "Requiere revisión."
                    ),
                ),
            )

        return PartialEvaluation(
            status="RECHAZADO",
            rule=self.name,
            alert=Alert(
                code=self.name,
                message=f"Gasto de '{expense.category}' excede el límite permitido.",
            ),
        )
