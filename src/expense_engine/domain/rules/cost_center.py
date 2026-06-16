"""Regla 3 — Regla cruzada de centro de costo."""

from __future__ import annotations

from expense_engine.domain.models import Alert
from expense_engine.domain.rules.base import EvaluationContext, PartialEvaluation


class CostCenterRule:
    """Rechaza un gasto si su categoría está prohibida para el centro de costo del empleado.

    Devuelve `None` si ninguna regla cruzada de la política aplica.
    """

    name = "POLITICA_CENTRO_COSTO"

    def evaluate(self, ctx: EvaluationContext) -> PartialEvaluation | None:
        category = ctx.normalized_expense.expense.category
        cost_center = ctx.employee.cost_center

        for rule in ctx.policy.cost_center_rules:
            if rule.cost_center == cost_center and rule.prohibited_category == category:
                return PartialEvaluation(
                    status="RECHAZADO",
                    rule=self.name,
                    alert=Alert(
                        code=self.name,
                        message=f"El C.C. '{cost_center}' no puede reportar '{category}'.",
                    ),
                )

        return None
