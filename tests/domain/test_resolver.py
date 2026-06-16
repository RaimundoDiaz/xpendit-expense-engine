"""Tests del resolvedor — la tabla de prioridades del estado final."""

from __future__ import annotations

from expense_engine.domain.models import Alert
from expense_engine.domain.resolver import resolve
from expense_engine.domain.rules.base import PartialEvaluation


def test_empty_defaults_to_pendiente_without_alerts() -> None:
    result = resolve("g_x", [])
    assert result.status == "PENDIENTE"
    assert result.alerts == []


def test_any_rejected_wins() -> None:
    evaluations = [
        PartialEvaluation(status="APROBADO", rule="A"),
        PartialEvaluation(status="PENDIENTE", rule="B"),
        PartialEvaluation(status="RECHAZADO", rule="C"),
    ]
    assert resolve("g_x", evaluations).status == "RECHAZADO"


def test_pending_beats_approved() -> None:
    evaluations = [
        PartialEvaluation(status="APROBADO", rule="A"),
        PartialEvaluation(status="PENDIENTE", rule="B"),
    ]
    assert resolve("g_x", evaluations).status == "PENDIENTE"


def test_all_approved_is_approved() -> None:
    evaluations = [
        PartialEvaluation(status="APROBADO", rule="A"),
        PartialEvaluation(status="APROBADO", rule="B"),
    ]
    assert resolve("g_x", evaluations).status == "APROBADO"


def test_collects_all_alerts() -> None:
    evaluations = [
        PartialEvaluation(status="PENDIENTE", rule="A", alert=Alert(code="X", message="x")),
        PartialEvaluation(status="RECHAZADO", rule="B", alert=Alert(code="Y", message="y")),
        PartialEvaluation(status="APROBADO", rule="C"),  # sin alerta
    ]
    result = resolve("g_x", evaluations)
    assert result.status == "RECHAZADO"
    assert [a.code for a in result.alerts] == ["X", "Y"]
