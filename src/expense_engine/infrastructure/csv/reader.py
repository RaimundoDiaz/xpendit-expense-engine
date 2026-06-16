"""Lector de gastos desde CSV.

Cada fila del CSV trae columnas en español y contiene tanto el gasto como el empleado.
Pydantic las parsea al dominio (en inglés) vía `validation_alias`. Las filas malformadas
se omiten y se reportan, sin tumbar el lote completo (los datos vienen de un sistema
antiguo y pueden estar "sucios").
"""

from __future__ import annotations

import csv
from dataclasses import dataclass

from pydantic import ValidationError

from expense_engine.domain.models import Employee, Expense, ExpenseRecord


@dataclass(frozen=True)
class RowError:
    """Una fila que no se pudo parsear."""

    line: int
    message: str


@dataclass(frozen=True)
class CsvReadResult:
    """Resultado de leer el CSV: registros válidos + filas omitidas."""

    records: list[ExpenseRecord]
    errors: list[RowError]


def read_records(path: str) -> CsvReadResult:
    """Lee el CSV y devuelve los registros válidos y los errores de parseo."""
    records: list[ExpenseRecord] = []
    errors: list[RowError] = []

    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        # line 1 es el encabezado; los datos empiezan en la línea 2.
        for line, row in enumerate(reader, start=2):
            try:
                expense = Expense.model_validate(row)
                employee = Employee.model_validate(row)
            except ValidationError as exc:
                errors.append(RowError(line=line, message=str(exc)))
                continue
            records.append(ExpenseRecord(expense=expense, employee=employee))

    return CsvReadResult(records=records, errors=errors)
