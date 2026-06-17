#!/usr/bin/env bash
# setup.sh — prepara el proyecto y lo deja listo para correr.
#
# Determinista y sin IA: crea el venv, instala dependencias (dev + API + paquete editable),
# crea .env.local desde el ejemplo si falta, y verifica con pytest + pyright.
# La skill `preparar-proyecto` simplemente ejecuta este script. Es trabajo por iniciativa
# propia (ver docs/08-extras-iniciativa.md).
set -euo pipefail

cd "$(dirname "$0")"

# 1. Elegir un intérprete Python 3.12+
PY=""
for cand in python3.12 python3 python; do
  if command -v "$cand" >/dev/null 2>&1 \
     && "$cand" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] >= (3, 12) else 1)'; then
    PY="$cand"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "ERROR: se requiere Python 3.12+ y no se encontró en el PATH." >&2
  exit 1
fi
echo "→ Usando $("$PY" --version)"

# 2. Crear el entorno virtual si no existe
if [ ! -d .venv ]; then
  echo "→ Creando entorno virtual en .venv"
  "$PY" -m venv .venv
fi
VENV_PY=".venv/bin/python"

# 3. Instalar dependencias (dev para tests/pyright + API extra + paquete editable)
echo "→ Instalando dependencias"
"$VENV_PY" -m pip install --quiet --upgrade pip
"$VENV_PY" -m pip install --quiet -r requirements-dev.txt
"$VENV_PY" -m pip install --quiet -r requirements-api.txt
"$VENV_PY" -m pip install --quiet -e .

# 4. Crear .env.local desde el ejemplo si falta
if [ ! -f .env.local ]; then
  cp .env.example .env.local
  echo "→ Creado .env.local — completa 'open_exchange_app_id' para usar tasas reales."
fi

# 5. Verificar
echo "→ Corriendo tests"
"$VENV_PY" -m pytest -q
echo "→ Type-check (pyright strict)"
"$VENV_PY" -m pyright

cat <<'EOF'

✅ Proyecto listo.
   Activa el entorno:   source .venv/bin/activate
   Corre el analizador: python -m expense_engine.cli.analyze "Desafío técnico — Xpendit/gastos_historicos.csv"
   Levanta la API:      uvicorn expense_engine.api.app:app --reload
EOF
