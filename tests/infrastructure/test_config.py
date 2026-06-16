"""Tests de la carga de la API key desde el entorno."""

from __future__ import annotations

from pathlib import Path

import pytest

from expense_engine.infrastructure.config import ENV_VAR, MissingApiKeyError, load_app_id


def test_loads_app_id_from_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_VAR, raising=False)
    env_file = tmp_path / ".env.local"
    env_file.write_text(f"{ENV_VAR}=ABC123\n", encoding="utf-8")

    assert load_app_id(str(env_file)) == "ABC123"


def test_missing_app_id_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_VAR, raising=False)
    empty = tmp_path / "empty.env"
    empty.write_text("", encoding="utf-8")

    with pytest.raises(MissingApiKeyError):
        load_app_id(str(empty))
