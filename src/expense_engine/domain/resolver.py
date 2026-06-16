"""Resolvedor del estado final a partir de las evaluaciones parciales.

Tabla de prioridades (del enunciado):
  1. Si CUALQUIER regla gatilla RECHAZADO → RECHAZADO.
  2. Si ninguna RECHAZADO y al menos una PENDIENTE → PENDIENTE.
  3. Si ninguna RECHAZADO ni PENDIENTE y al menos una APROBADO → APROBADO.
  4. Por defecto (ninguna regla aplica) → PENDIENTE, sin alertas.

Las alertas del resultado son TODAS las alertas producidas por las reglas (es una lista).
"""

from __future__ import annotations

from collections.abc import Sequence

from expense_engine.domain.models import Alert, Status, ValidationResult
from expense_engine.domain.rules.base import PartialEvaluation


def resolve(expense_id: str, evaluations: Sequence[PartialEvaluation]) -> ValidationResult:
    """Combina las evaluaciones parciales en un resultado final."""
    if not evaluations:
        # Por defecto: ninguna regla aplicó.
        return ValidationResult(expense_id=expense_id, status="PENDIENTE", alerts=[])

    statuses = {evaluation.status for evaluation in evaluations}
    final_status: Status
    if "RECHAZADO" in statuses:
        final_status = "RECHAZADO"
    elif "PENDIENTE" in statuses:
        final_status = "PENDIENTE"
    else:
        final_status = "APROBADO"

    alerts: list[Alert] = [e.alert for e in evaluations if e.alert is not None]
    return ValidationResult(expense_id=expense_id, status=final_status, alerts=alerts)
