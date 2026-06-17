"""Tests del lector de CSV."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from expense_engine.infrastructure.csv.reader import iter_records, read_records

_HEADER = "gasto_id,empleado_id,empleado_nombre,empleado_apellido,empleado_cost_center,categoria,monto,moneda,fecha"


def _write_csv(tmp_path: Path, *rows: str) -> str:
    content = "\n".join([_HEADER, *rows]) + "\n"
    path = tmp_path / "gastos.csv"
    path.write_text(content, encoding="utf-8")
    return str(path)


def test_parses_valid_rows(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "g_001,e_002,Bruno,Soto,sales_team,food,50,USD,2026-06-01",
        "g_004,e_005,Eva,Luna,sales_team,food,81000,CLP,2026-05-17",
    )
    result = read_records(path)

    assert result.errors == []
    assert len(result.records) == 2

    first = result.records[0]
    assert first.expense.id == "g_001"
    assert first.expense.amount == Decimal("50")
    assert first.expense.currency == "USD"
    assert first.employee.first_name == "Bruno"
    assert first.employee.cost_center == "sales_team"


def test_negative_amount_is_valid_not_an_error(tmp_path: Path) -> None:
    # Un monto negativo es un dato (anomalía), no un error de parseo.
    path = _write_csv(
        tmp_path, "g_x,e_001,Ana,Reyes,finance,food,-50,USD,2026-06-01"
    )
    result = read_records(path)
    assert result.errors == []
    assert result.records[0].expense.amount == Decimal("-50")


def test_malformed_row_is_skipped_and_reported(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "g_ok,e_001,Ana,Reyes,finance,food,50,USD,2026-06-01",
        "g_bad,e_002,Bruno,Soto,sales_team,food,NOT_A_NUMBER,USD,2026-06-01",
    )
    result = read_records(path)

    assert len(result.records) == 1
    assert result.records[0].expense.id == "g_ok"
    assert len(result.errors) == 1
    assert result.errors[0].line == 3


def test_iter_records_streams_valid_rows_and_skips_malformed(tmp_path: Path) -> None:
    # El generador (extra, streaming §3) yield solo los válidos, omitiendo los malos.
    path = _write_csv(
        tmp_path,
        "g_ok1,e_001,Ana,Reyes,finance,food,50,USD,2026-06-01",
        "g_bad,e_002,Bruno,Soto,sales_team,food,NOT_A_NUMBER,USD,2026-06-01",
        "g_ok2,e_003,Eva,Luna,sales_team,food,81000,CLP,2026-05-17",
    )
    ids = [record.expense.id for record in iter_records(path)]
    assert ids == ["g_ok1", "g_ok2"]
