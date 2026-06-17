# 08 — Extras por iniciativa propia (fuera del alcance del desafío)

> **Para el equipo evaluador de Xpendit:** todo lo listado en este documento es trabajo
> que agregamos **por iniciativa propia**. **No** formaba parte del enunciado del desafío
> (Partes 1, 2 y 3). Lo documentamos explícitamente para que quede claro que, si ven
> código o archivos "de más", **no es un error ni relleno**: es trabajo deliberado pensado
> para el siguiente paso del proceso —la entrevista en vivo, que *evolucionará* este
> código— y para demostrar cómo el diseño escala.
>
> El alcance obligatorio del desafío está intacto y entregado tal como se pidió
> (ver [`05-deliverables.md`](05-deliverables.md)). Esto es **adicional**.

## Por qué lo agregamos
El enunciado dice que la entrevista en vivo evolucionará el código y que el diseño
extensible es clave. En vez de esperar a la entrevista, dejamos **pavimentado el camino**:
identificamos los ejes de escala (ver [`07-escalabilidad.md`](07-escalabilidad.md)) y, donde
el riesgo era bajo y aditivo, lo implementamos; donde podía romper el contrato del enunciado
o sonar a over-engineering, lo **diseñamos y documentamos** sin forzarlo.

## Catálogo de extras

### 1. Scaffold de reglas (`domain/rules/_template.py` + test espejo)
Plantilla comentada para crear reglas nuevas en 3 pasos (copiar → rellenar → registrar).
Es inerte (devuelve `None`), así que no altera ningún resultado. **Parte del repo.**

### 2. Provider de tasas con fallback/retry (`infrastructure/exchange_rates/`)
Adaptador que implementa el mismo puerto `ExchangeRateProvider` y envuelve a otro provider
para dar resiliencia (reintentos / proveedor de respaldo). Demuestra el eje §2 de
escalabilidad. **Parte del repo.**

### 3. Lectura streaming del CSV (`infrastructure/csv/reader.py`)
Variante generadora que no materializa todo el archivo en memoria — habilita procesar lotes
grandes (eje §3). Aditiva: la API original `read_records` se mantiene. **Parte del repo.**

### 4. Scaffold de API HTTP (`api/`)
Endpoints FastAPI (`POST /validate`, `POST /analyze`) que exponen el motor reusando la capa
`application` **sin tocar el dominio** (eje §5). Provider y política son inyectables
(`Depends`), así que se testea sin red ni secretos. Es un scaffold de demostración, no un
servicio productivo. **Parte del repo**, con dependencias **opcionales** (no requeridas para
Partes 1–3):

```bash
pip install -r requirements-api.txt        # o:  pip install -e ".[api]"
uvicorn expense_engine.api.app:app --reload
```

### 5. Tooling de Claude Code (`.claude/`) — *versionado a propósito*
Como el evaluador **fomenta el uso de IA**, versionamos nuestro tooling para que se vea cómo
trabajamos. Lo dejamos en el repo de forma deliberada (lo único que queda local es `CLAUDE.md`
y los ajustes locales de la herramienta).

- **Skills** (`.claude/skills/`) — automatizan el scaffolding repetitivo durante la evolución
  del código: `nueva-regla`, `nuevo-provider`, `nueva-anomalia`, `exponer-api`, y
  `preparar-proyecto` (ver item 6).
- **Agentes** (`.claude/agents/`) — revisores especializados, complemento de las skills:
  - `revisor-de-reglas` — audita una regla nueva (3 estados, alertas, registro, tests).
  - `guardian-arquitectura` — verifica los límites hexagonales (dominio puro, deps hacia adentro).
  - `qa-y-pruebas` — QA del código: corre la suite + pyright, detecta huecos y escribe tests.

### 6. Setup en un comando (`setup.sh` + skill `preparar-proyecto`)
`setup.sh` deja el proyecto listo (venv, dependencias, `.env.local`, verificación con tests +
pyright) de forma **determinista y sin IA**. La skill `preparar-proyecto` lo ejecuta e
interpreta para un flujo "un solo prompt" con Claude Code. Ver el inicio rápido en el `README.md`.

### 7. Integración continua (`.github/workflows/ci.yml`)
Workflow de GitHub Actions que corre `pytest` + `pyright` (strict) en cada push y PR a `main`.
Refuerza la señal de calidad y evita regresiones. **Parte del repo.**

### 8. Documentación de escalabilidad y wiki
- [`07-escalabilidad.md`](07-escalabilidad.md): mapa de ejes de crecimiento y seams.
- Una **wiki de GitHub** con toda la documentación navegable.

## Qué NO tocamos
El núcleo del desafío permanece fiel al enunciado:
- Contrato de salida del validador: `{gasto_id, status, alertas}` sin cambios.
- Las 3 reglas originales, el resolvedor de prioridades y el flujo de Partes 1–3.
- La política `policy.json` y el formato del CSV.

Los seams que **romperían** ese contrato (traza de reglas en el resultado, versionado de
política) quedaron **diseñados pero no implementados** — documentados en
[`07-escalabilidad.md`](07-escalabilidad.md), listos para construir en vivo si se piden.
