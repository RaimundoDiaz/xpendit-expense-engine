---
name: preparar-proyecto
description: Prepara e instala el proyecto Xpendit de cero y lo deja listo para correr — crea el venv, instala dependencias, configura .env.local y verifica con tests + pyright. Úsala al clonar el repo o cuando pidan "instala / prepara / deja listo / setup del proyecto".
---

# Preparar el proyecto Xpendit

Deja el repo listo para ejecutar. La **fuente de verdad es `setup.sh`** (determinista, también
sirve sin IA); esta skill lo ejecuta, interpreta el resultado y guía al usuario.

## Pasos

1. Ejecuta el script de setup desde la raíz del repo:
   ```bash
   bash setup.sh
   ```
   Hace: detecta Python 3.12+, crea `.venv`, instala dev + API + el paquete editable, crea
   `.env.local` desde `.env.example` si falta, y verifica con `pytest` + `pyright`.

2. Si `setup.sh` falla, diagnostica con la salida real (no asumas):
   - **Python < 3.12 o ausente:** pide instalar Python 3.12+ y reintentar.
   - **Fallo de red en `pip`:** reintenta; reporta qué paquete falló.
   - **Tests o pyright en rojo:** muestra la salida; **no** digas que está listo si no lo está.

3. Reporta el resultado de forma concreta: cuántos tests pasaron, si pyright quedó limpio, y los
   comandos para usar el proyecto:
   - Tests: `pytest`
   - Analizador de lotes: `python -m expense_engine.cli.analyze "Desafío técnico — Xpendit/gastos_historicos.csv"`
   - API (extra): `uvicorn expense_engine.api.app:app --reload`

4. Recuérdale que para **tasas reales** debe completar `open_exchange_app_id` en `.env.local`.
   Los tests pasan sin la key (usan un proveedor mock); solo el CLI/API contra la API real la necesitan.

## Nota
`setup.sh` y esta skill son trabajo por iniciativa propia (ver `docs/08-extras-iniciativa.md`).
