# 05 — Entregables y Entrega

**Forma de entrega**: responder el correo a Nicolás con link a repo Git (GitHub/GitLab) o un `.zip`. Plazo: martes 23 jun 2026, 14:57 (Chile).

## Entregables finales obligatorios
1. Todo el código fuente de Partes 1, 2 y 3.
2. Tests unitarios de la Parte 1 (entregable más importante — cada regla y cada estado).
3. `ANALISIS.md` (Parte 3): desglose por estado, anomalías con ejemplos, explicación de optimización N+1.
4. Video ≤ 1 minuto resumiendo hallazgos de Parte 3.
5. `README.md` con:
   - Instalación (`pip install -r requirements.txt`, idealmente en un venv).
   - Configuración: cómo proveer la API Key de Open Exchange Rates (vía `.env` / `.env.local`; incluir `.env.example`).
   - Cómo correr los tests (`pytest`).
   - Cómo correr el analizador de lotes (ej. `python analizar.py`).

## Recordatorios de evaluación
- Manejo de secretos: `.env.local` gitignored, nunca commitear la key.
- Manejo de errores y separación de responsabilidades.
- Calidad de tests.
- La entrevista en vivo **evolucionará** este código → diseño extensible es clave.
