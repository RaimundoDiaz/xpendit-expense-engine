"""Tests del analizador de lotes (end-to-end con proveedor mock)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from expense_engine.application.batch_analyzer import analyze
from expense_engine.domain.models import Employee, Expense, ExpenseRecord, Policy
from expense_engine.infrastructure.exchange_rates.mock_provider import MockExchangeRateProvider

REFERENCE_DATE = date(2026, 6, 16)

POLICY = Policy.model_validate(
    {
        "moneda_base": "USD",
        "limite_antiguedad": {"pendiente_dias": 30, "rechazado_dias": 60},
        "limites_por_categoria": {"food": {"aprobado_hasta": 100, "pendiente_hasta": 150}},
        "reglas_centro_costo": [
            {"cost_center": "core_engineering", "categoria_prohibida": "food"}
        ],
    }
)


def _record(
    expense_id: str,
    amount: str,
    *,
    currency: str = "USD",
    date_str: str = "2026-06-01",
    category: str = "food",
    cost_center: str = "sales_team",
) -> ExpenseRecord:
    expense = Expense(
        id=expense_id, amount=Decimal(amount), currency=currency, date=date_str, category=category
    )
    employee = Employee(id="e_1", first_name="N", last_name="N", cost_center=cost_center)
    return ExpenseRecord(expense=expense, employee=employee)


def test_aggregates_statuses_and_anomalies() -> None:
    records = [
        _record("g_001", "50"),  # APROBADO
        _record("g_002", "120"),  # PENDIENTE (excede aprobado)
        _record("g_011", "55", cost_center="core_engineering"),  # RECHAZADO (regla cruzada)
        _record("g_023", "50", date_str="2025-12-31"),  # RECHAZADO (antigüedad)
        _record("g_042", "90", date_str="2026-06-06"),  # duplicado
        _record("g_043", "90", date_str="2026-06-06"),  # duplicado
        _record("g_neg", "-10"),  # monto negativo
    ]
    provider = MockExchangeRateProvider()  # todo en USD, sin conversión

    report = analyze(records, POLICY, provider, REFERENCE_DATE)

    # APROBADO: g_001, g_042, g_043, g_neg (el negativo pasa las reglas: -10 <= 100;
    # se detecta como anomalía aparte, no por el motor).
    assert report.status_counts["APROBADO"] == 4
    assert report.status_counts["PENDIENTE"] == 1  # g_002
    assert report.status_counts["RECHAZADO"] == 2  # g_011 (cruzada), g_023 (antigüedad)
    assert sum(report.status_counts.values()) == len(records)

    assert len(report.duplicates) == 1
    assert report.duplicates[0].expense_ids == ["g_042", "g_043"]

    assert [e.id for e in report.negatives] == ["g_neg"]
