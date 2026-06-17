"""PLANTILLA de regla — copia este archivo para crear una regla nueva.

Cómo agregar una regla (3 pasos):
  1. Copia este archivo a `mi_regla.py` y renombra la clase (p. ej. `MiRegla`).
  2. Rellena `name`, la lógica de `evaluate` y borra lo que no uses.
  3. Regístrala en `registry.py` añadiéndola a `DEFAULT_RULES`.
     (El motor `engine.py` y el resolvedor `resolver.py` NO se tocan — Open/Closed.)

Convenciones que toda regla cumple:
  - Devuelve `None` cuando la regla NO aplica al gasto (no opina).
  - Devuelve un `PartialEvaluation` con su `status` cuando sí aplica.
  - Adjunta una `Alert` salvo para el caso "todo OK" (APROBADO sin alerta).
  - `name` se usa como `code` de la alerta y como id de la regla: en MAYÚSCULAS.

Este template es INERTE a propósito: devuelve `None` siempre, así que si lo
registraras por error no cambiaría ningún resultado. Borra ese `return None` final
cuando implementes tu lógica.
"""

from __future__ import annotations

from expense_engine.domain.models import Alert
from expense_engine.domain.rules.base import EvaluationContext, PartialEvaluation


class TemplateRule:
    """Describe en una línea QUÉ valida la regla y cuándo NO aplica (devuelve None)."""

    # Identificador de la regla. Sale como `codigo` en las alertas. Renómbralo.
    name = "TEMPLATE_RULE"

    def evaluate(self, ctx: EvaluationContext) -> PartialEvaluation | None:
        # --- 1. Datos disponibles en el contexto (usa solo los que necesites) ---
        expense = ctx.normalized_expense.expense       # gasto original (moneda/monto originales)
        amount_base = ctx.normalized_expense.amount_base  # monto ya convertido a moneda base
        _ = ctx.employee                               # empleado que reportó (p. ej. cost_center)
        _ = ctx.policy                                 # política como data (umbrales, listas)
        _ = ctx.reference_date                          # "hoy" inyectado, para cálculos de fecha
        _ = (expense, amount_base)                      # (borra estas líneas al implementar)

        # --- 2. ¿Aplica la regla? Si no, no opines. ---
        # Ejemplo: si la política no define lo que esta regla necesita, devuelve None.
        # if <la regla no aplica a este gasto>:
        #     return None

        # --- 3. Caso APROBADO: opina sin alerta. ---
        # if <condición OK>:
        #     return PartialEvaluation(status="APROBADO", rule=self.name)

        # --- 4. Caso PENDIENTE: opina con una alerta explicando por qué. ---
        # if <condición límite>:
        #     return PartialEvaluation(
        #         status="PENDIENTE",
        #         rule=self.name,
        #         alert=Alert(code=self.name, message="Requiere revisión: ..."),
        #     )

        # --- 5. Caso RECHAZADO: opina con una alerta. ---
        # return PartialEvaluation(
        #     status="RECHAZADO",
        #     rule=self.name,
        #     alert=Alert(code=self.name, message="Rechazado porque ..."),
        # )

        # Template inerte: bórralo cuando implementes los casos de arriba.
        return None
