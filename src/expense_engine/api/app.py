"""Scaffold de API HTTP (FastAPI) — EXTRA por iniciativa propia.

NO es parte del desafío (ver docs/08-extras-iniciativa.md). Demuestra el eje §5 de
docs/07-escalabilidad.md: una API es *otro adaptador de entrada*, igual que el CLI, y
reusa la capa `application` SIN tocar el dominio.

El provider de tasas y la política son inyectables (`Depends`) para poder testear sin red
ni secretos (los tests los sobreescriben con un mock).

Levantar (requiere el extra `api`):  uvicorn expense_engine.api.app:app --reload
"""

from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from expense_engine.application.batch_analyzer import analyze
from expense_engine.application.ports import ExchangeRateProvider
from expense_engine.domain.engine import validate_expense
from expense_engine.domain.models import (
    Employee,
    Expense,
    ExpenseRecord,
    NormalizedExpense,
    Policy,
)
from expense_engine.domain.rules.base import EvaluationContext
from expense_engine.infrastructure.config import load_app_id
from expense_engine.infrastructure.exchange_rates.openexchange_client import (
    OpenExchangeRatesClient,
)


class RecordIn(BaseModel):
    """Una fila de entrada: el gasto y el empleado que lo reportó (alias en español)."""

    gasto: Expense
    empleado: Employee


class ValidateRequest(RecordIn):
    """Cuerpo de `POST /validate`: un gasto + empleado, con fecha de referencia opcional."""

    fecha_referencia: date | None = None


class AnalyzeRequest(BaseModel):
    """Cuerpo de `POST /analyze`: un lote de gastos."""

    gastos: list[RecordIn]
    fecha_referencia: date | None = None


@lru_cache
def get_policy() -> Policy:
    """Carga la política desde `policy.json` (cacheada). Sobreescribible en tests."""
    with open("policy.json", encoding="utf-8") as handle:
        return Policy.model_validate(json.load(handle))


@lru_cache
def get_provider() -> ExchangeRateProvider:
    """Construye el cliente real de tasas (cacheado). Sobreescribible en tests."""
    return OpenExchangeRatesClient(app_id=load_app_id())


PolicyDep = Annotated[Policy, Depends(get_policy)]
ProviderDep = Annotated[ExchangeRateProvider, Depends(get_provider)]

app = FastAPI(title="Xpendit — Motor de Reglas de Gastos (scaffold API, extra)")


@app.post("/validate")
def validate(body: ValidateRequest, policy: PolicyDep, provider: ProviderDep) -> dict[str, object]:
    """Valida un gasto y devuelve `{gasto_id, status, alertas}` (contrato del enunciado)."""
    amount_base = provider.convert(body.gasto.amount, body.gasto.currency, body.gasto.date)
    ctx = EvaluationContext(
        normalized_expense=NormalizedExpense(expense=body.gasto, amount_base=amount_base),
        employee=body.empleado,
        policy=policy,
        reference_date=body.fecha_referencia or date.today(),
    )
    return validate_expense(ctx).model_dump(by_alias=True)


@app.post("/analyze")
def analyze_batch(body: AnalyzeRequest, policy: PolicyDep, provider: ProviderDep) -> dict[str, object]:
    """Analiza un lote: resultados por gasto + conteo por estado + anomalías."""
    records = [ExpenseRecord(expense=r.gasto, employee=r.empleado) for r in body.gastos]
    report = analyze(records, policy, provider, body.fecha_referencia or date.today())
    return {
        "resultados": [r.model_dump(by_alias=True) for r in report.results],
        "conteo_por_estado": report.status_counts,
        "duplicados": len(report.duplicates),
        "negativos": len(report.negatives),
    }
