"""Carga de configuración / secretos desde el entorno.

La API key de Open Exchange Rates se lee de una variable de entorno (poblada desde
`.env.local`). Nunca se hardcodea ni se commitea.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

ENV_VAR = "open_exchange_app_id"


class MissingApiKeyError(RuntimeError):
    """Se lanza cuando no se encuentra la API key de Open Exchange Rates."""


def load_app_id(dotenv_path: str = ".env.local") -> str:
    """Carga el `app_id` desde el archivo dado (o desde el entorno ya existente).

    Lanza `MissingApiKeyError` si no está definido, con un mensaje accionable.
    """
    load_dotenv(dotenv_path)
    app_id = os.environ.get(ENV_VAR)
    if not app_id:
        raise MissingApiKeyError(
            f"Falta la API key. Define '{ENV_VAR}' en '{dotenv_path}' "
            "(copia .env.example y completa tu App ID de Open Exchange Rates)."
        )
    return app_id
