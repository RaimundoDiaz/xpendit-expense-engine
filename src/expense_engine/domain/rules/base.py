"""Contratos del patrón Strategy para las reglas.

Cada regla es una unidad independiente que "opina" sobre un gasto devolviendo una
`PartialEvaluation` (o `None` si no aplica). El motor recolecta esas opiniones y el
resolvedor decide el estado final. Agregar una regla = crear una clase que cumpla el
protocolo `Rule` y registrarla; ni el motor ni el resolvedor cambian (Open/Closed).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable

from expense_engine.domain.models import Alert, Employee, NormalizedExpense, Policy, Status


@dataclass(frozen=True)
class EvaluationContext:
    """Todo lo que una regla podría necesitar para evaluar un gasto.

    Pasar un contexto (en vez de N parámetros sueltos) significa que agregar una regla
    que requiere un dato nuevo NO cambia la firma de `Rule.evaluate`.
    """

    normalized_expense: NormalizedExpense
    employee: Employee
    policy: Policy
    reference_date: date  # el "hoy" para calcular la antigüedad (inyectado, reproducible)


@dataclass(frozen=True)
class PartialEvaluation:
    """La opinión de una regla: un estado, opcionalmente con una alerta."""

    status: Status
    rule: str
    alert: Alert | None = None


@runtime_checkable
class Rule(Protocol):
    """Interfaz que toda regla debe cumplir (tipado estructural)."""

    name: str

    def evaluate(self, ctx: EvaluationContext) -> PartialEvaluation | None:
        """Devuelve la opinión de la regla, o `None` si la regla no aplica al gasto."""
        ...
