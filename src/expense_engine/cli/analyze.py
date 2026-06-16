"""CLI del analizador de lotes.

Uso:
    python -m expense_engine.cli.analyze <ruta_csv> [--policy policy.json]
        [--reference-date YYYY-MM-DD] [--json]

Ensambla las 3 partes: lee el CSV, convierte monedas con la API real (cacheada por
fecha), valida con el motor de reglas y resume el desglose por estado y las anomalías.
"""

from __future__ import annotations

import argparse
import json
from datetime import date

from expense_engine.application.batch_analyzer import BatchReport, analyze
from expense_engine.domain.models import Policy
from expense_engine.infrastructure.config import MissingApiKeyError, load_app_id
from expense_engine.infrastructure.csv.reader import CsvReadResult, read_records
from expense_engine.infrastructure.exchange_rates.openexchange_client import (
    ExchangeRateError,
    OpenExchangeRatesClient,
)


def _load_policy(path: str) -> Policy:
    with open(path, encoding="utf-8") as handle:
        return Policy.model_validate(json.load(handle))


def _print_report(report: BatchReport, read_result: CsvReadResult, total: int) -> None:
    print(f"\n=== Análisis de {total} gastos ===\n")

    print("Desglose por estado:")
    for status, count in report.status_counts.items():
        print(f"  {status:10} {count}")

    print(f"\nDuplicados exactos (monto+moneda+fecha): {len(report.duplicates)} grupo(s)")
    for group in report.duplicates:
        ids = ", ".join(group.expense_ids)
        print(f"  {group.amount} {group.currency} en {group.date}: {ids}")

    print(f"\nMontos negativos: {len(report.negatives)}")
    for expense in report.negatives:
        print(f"  {expense.id}: {expense.amount} {expense.currency}")

    if read_result.errors:
        print(f"\nFilas omitidas (malformadas): {len(read_result.errors)}")
        for row_error in read_result.errors:
            print(f"  línea {row_error.line}: {row_error.message}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analizador de lotes de gastos (Xpendit).")
    parser.add_argument("csv_path", help="Ruta al CSV de gastos.")
    parser.add_argument("--policy", default="policy.json", help="Ruta al JSON de política.")
    parser.add_argument(
        "--reference-date",
        default=None,
        help="Fecha de referencia (YYYY-MM-DD) para la antigüedad. Por defecto: hoy.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Imprime los resultados por gasto como JSON."
    )
    args = parser.parse_args(argv)

    csv_path: str = args.csv_path
    policy_path: str = args.policy
    ref_str: str | None = args.reference_date
    as_json: bool = args.json

    reference_date = date.fromisoformat(ref_str) if ref_str else date.today()

    try:
        policy = _load_policy(policy_path)
        app_id = load_app_id()
        provider = OpenExchangeRatesClient(app_id=app_id)
        read_result = read_records(csv_path)
        report = analyze(read_result.records, policy, provider, reference_date)
    except (MissingApiKeyError, ExchangeRateError, FileNotFoundError) as exc:
        print(f"Error: {exc}")
        return 1

    if as_json:
        payload = [result.model_dump(by_alias=True) for result in report.results]
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    else:
        _print_report(report, read_result, total=len(read_result.records))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
