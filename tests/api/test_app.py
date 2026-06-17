"""Tests del scaffold de API (extra). Se omiten si el extra `api` no está instalado."""

# El TestClient de Starlette expone tipos parcialmente desconocidos según la versión de
# httpx instalada; relajamos esos dos chequeos SOLO en este archivo de test (extra).
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal

import pytest

pytest.importorskip("fastapi")  # el scaffold de API es un extra opcional

from fastapi.testclient import TestClient  # noqa: E402

from expense_engine.api.app import app, get_policy, get_provider  # noqa: E402
from expense_engine.infrastructure.exchange_rates.mock_provider import (  # noqa: E402
    MockExchangeRateProvider,
)
from tests.helpers import build_policy  # noqa: E402


@pytest.fixture
def client() -> Iterator[TestClient]:
    # Sin red ni secretos: provider mock + política de ejemplo inyectados.
    app.dependency_overrides[get_provider] = lambda: MockExchangeRateProvider(
        {"CLP": Decimal("900")}
    )
    app.dependency_overrides[get_policy] = build_policy
    yield TestClient(app)
    app.dependency_overrides.clear()


def _record(gasto_id: str, monto: str, categoria: str = "food") -> dict[str, object]:
    return {
        "gasto": {
            "gasto_id": gasto_id,
            "monto": monto,
            "moneda": "USD",
            "fecha": "2026-06-01",
            "categoria": categoria,
        },
        "empleado": {
            "empleado_id": "e1",
            "empleado_nombre": "Ana",
            "empleado_apellido": "Reyes",
            "empleado_cost_center": "sales_team",
        },
    }


def test_validate_returns_contract_shape(client: TestClient) -> None:
    body = _record("g1", "50") | {"fecha_referencia": "2026-06-16"}
    response = client.post("/validate", json=body)

    assert response.status_code == 200
    data = response.json()
    assert data == {"gasto_id": "g1", "status": "APROBADO", "alertas": []}


def test_validate_rejects_malformed_amount(client: TestClient) -> None:
    body = _record("g_bad", "NOT_A_NUMBER") | {"fecha_referencia": "2026-06-16"}
    response = client.post("/validate", json=body)
    assert response.status_code == 422  # Pydantic valida el cuerpo


def test_analyze_counts_statuses(client: TestClient) -> None:
    body = {
        "fecha_referencia": "2026-06-16",
        "gastos": [_record("g1", "50"), _record("g2", "999")],
    }
    response = client.post("/analyze", json=body)

    assert response.status_code == 200
    data = response.json()
    assert data["conteo_por_estado"]["APROBADO"] == 1   # $50 food
    assert data["conteo_por_estado"]["RECHAZADO"] == 1   # $999 food > límite
