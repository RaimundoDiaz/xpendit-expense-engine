"""Helpers tipados para construir objetos del dominio en los tests."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from expense_engine.domain.models import (
    Employee,
    Expense,
    NormalizedExpense,
    Policy,
)
from expense_engine.domain.rules.base import EvaluationContext

# "Hoy" fijo para que los tests de antigüedad sean deterministas.
REFERENCE_DATE = date(2026, 6, 16)

# Política de ejemplo del enunciado (en español, como llega del JSON).
POLICY_DATA: dict[str, object] = {
    "moneda_base": "USD",
    "limite_antiguedad": {"pendiente_dias": 30, "rechazado_dias": 60},
    "limites_por_categoria": {
        "food": {"aprobado_hasta": 100, "pendiente_hasta": 150},
        "transport": {"aprobado_hasta": 200, "pendiente_hasta": 200},
    },
    "reglas_centro_costo": [
        {"cost_center": "core_engineering", "categoria_prohibida": "food"}
    ],
}


def build_policy() -> Policy:
    """Construye la política de ejemplo (ejercita el parseo por aliases en español)."""
    return Policy.model_validate(POLICY_DATA)


def build_context(
    *,
    amount_base: Decimal | str = "50",
    category: str = "food",
    currency: str = "USD",
    expense_date: str = "2026-06-01",
    cost_center: str = "sales_team",
    reference_date: date = REFERENCE_DATE,
    expense_id: str = "g_test",
    policy: Policy | None = None,
) -> EvaluationContext:
    """Arma un `EvaluationContext` listo para evaluar, con un gasto ya normalizado.

    `amount_base` es el monto en la moneda base (USD); para el dominio el monto
    original no influye, así que lo igualamos al normalizado por simplicidad.
    """
    amount = Decimal(str(amount_base))
    expense = Expense(
        id=expense_id,
        amount=amount,
        currency=currency,
        date=expense_date,
        category=category,
    )
    normalized = NormalizedExpense(expense=expense, amount_base=amount)
    employee = Employee(
        id="e_test", first_name="Test", last_name="User", cost_center=cost_center
    )
    return EvaluationContext(
        normalized_expense=normalized,
        employee=employee,
        policy=policy if policy is not None else build_policy(),
        reference_date=reference_date,
    )
