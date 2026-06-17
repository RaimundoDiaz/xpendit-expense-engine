"""Lector de gastos desde CSV.

Cada fila del CSV trae columnas en español y contiene tanto el gasto como el empleado.
Pydantic las parsea al dominio (en inglés) vía `validation_alias`. Las filas malformadas
se omiten y se reportan, sin tumbar el lote completo (los datos vienen de un sistema
antiguo y pueden estar "sucios").
"""

from __future__ import annotations

import csv
from collections.abc import Iterator, Mapping
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


def _parse_row(row: Mapping[str, str | None]) -> tuple[ExpenseRecord | None, str | None]:
    """Parsea una fila al dominio.

    Devuelve `(record, None)` si es válida, o `(None, mensaje)` si está malformada.
    """
    try:
        expense = Expense.model_validate(row)
        employee = Employee.model_validate(row)
    except ValidationError as exc:
        return None, str(exc)
    return ExpenseRecord(expense=expense, employee=employee), None


def iter_records(path: str) -> Iterator[ExpenseRecord]:
    """Itera los registros VÁLIDOS del CSV de a uno, sin cargar todo en memoria.

    Pensado para lotes grandes (eje de escala §3 en docs/07-escalabilidad.md): es un
    generador, así que el archivo se procesa en streaming. Las filas malformadas se omiten
    en silencio; si necesitas el detalle de los errores, usa `read_records`.
    """
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            record, _ = _parse_row(row)
            if record is not None:
                yield record


def read_records(path: str) -> CsvReadResult:
    """Lee el CSV y devuelve los registros válidos y los errores de parseo."""
    records: list[ExpenseRecord] = []
    errors: list[RowError] = []

    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        # line 1 es el encabezado; los datos empiezan en la línea 2.
        for line, row in enumerate(reader, start=2):
            record, error = _parse_row(row)
            if record is None:
                errors.append(RowError(line=line, message=error or ""))
                continue
            records.append(record)

    return CsvReadResult(records=records, errors=errors)
