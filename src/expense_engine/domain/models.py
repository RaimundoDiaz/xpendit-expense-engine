"""Modelos del dominio.

Estos modelos son el corazón del sistema y no dependen de ninguna infraestructura
(red, archivos, librerías de I/O). Usan Pydantic como *anti-corruption layer*:
los datos externos vienen en español (CSV / JSON de política) y se parsean a un dominio
en inglés mediante `validation_alias`; el resultado se serializa de vuelta con las llaves
exactas del enunciado (`gasto_id`, `status`, `alertas`, `codigo`, `mensaje`) vía
`serialization_alias`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Los tres estados posibles. Los VALORES los define el enunciado (en español).
Status = Literal["APROBADO", "PENDIENTE", "RECHAZADO"]


class Expense(BaseModel):
    """Un gasto reportado por un empleado."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    id: str = Field(validation_alias="gasto_id")
    amount: Decimal = Field(validation_alias="monto")
    currency: str = Field(validation_alias="moneda")
    date: str = Field(validation_alias="fecha")  # ISO: "2026-05-17"
    category: str = Field(validation_alias="categoria")


class Employee(BaseModel):
    """El empleado que reportó el gasto."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    id: str = Field(validation_alias="empleado_id")
    first_name: str = Field(validation_alias="empleado_nombre")
    last_name: str = Field(validation_alias="empleado_apellido")
    cost_center: str = Field(validation_alias="empleado_cost_center")


class AgeLimit(BaseModel):
    """Umbrales de antigüedad (en días) de la política."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    pending_days: int = Field(validation_alias="pendiente_dias")
    rejected_days: int = Field(validation_alias="rechazado_dias")


class CategoryLimit(BaseModel):
    """Límites de monto (en la moneda base) para una categoría."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    approved_up_to: Decimal = Field(validation_alias="aprobado_hasta")
    pending_up_to: Decimal = Field(validation_alias="pendiente_hasta")


class CostCenterRuleConfig(BaseModel):
    """Regla cruzada: un centro de costo tiene prohibida una categoría."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    cost_center: str
    prohibited_category: str = Field(validation_alias="categoria_prohibida")


def _empty_category_limits() -> dict[str, CategoryLimit]:
    return {}


def _empty_cost_center_rules() -> list[CostCenterRuleConfig]:
    return []


class Policy(BaseModel):
    """La política de la empresa: el conjunto de reglas, como DATA (no código)."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    base_currency: str = Field(validation_alias="moneda_base")
    age_limit: AgeLimit = Field(validation_alias="limite_antiguedad")
    category_limits: dict[str, CategoryLimit] = Field(
        validation_alias="limites_por_categoria", default_factory=_empty_category_limits
    )
    cost_center_rules: list[CostCenterRuleConfig] = Field(
        validation_alias="reglas_centro_costo", default_factory=_empty_cost_center_rules
    )


@dataclass(frozen=True)
class NormalizedExpense:
    """Un gasto con su monto ya convertido a la moneda base (USD).

    Conserva el `Expense` original intacto para trazabilidad (la moneda y el monto
    originales pueden importar para alertas y auditoría).
    """

    expense: Expense
    amount_base: Decimal


@dataclass(frozen=True)
class ExpenseRecord:
    """Un gasto junto al empleado que lo reportó (una fila del CSV)."""

    expense: Expense
    employee: Employee


@dataclass(frozen=True)
class NormalizedRecord:
    """Un registro cuyo gasto ya fue convertido a la moneda base."""

    normalized_expense: NormalizedExpense
    employee: Employee


class Alert(BaseModel):
    """Una alerta adjunta a un resultado. Se serializa como {codigo, mensaje}."""

    model_config = ConfigDict(frozen=True)

    code: str = Field(serialization_alias="codigo")
    message: str = Field(serialization_alias="mensaje")


def _empty_alerts() -> list[Alert]:
    return []


class ValidationResult(BaseModel):
    """El resultado de validar un gasto. Se serializa como {gasto_id, status, alertas}."""

    model_config = ConfigDict(frozen=True)

    expense_id: str = Field(serialization_alias="gasto_id")
    status: Status
    alerts: list[Alert] = Field(
        default_factory=_empty_alerts, serialization_alias="alertas"
    )
