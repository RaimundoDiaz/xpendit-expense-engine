# Xpendit — Motor de Reglas de Gastos

Prototipo del **Motor de Reglas de Gastos** de Xpendit: valida gastos contra una política
configurable (estados `APROBADO` / `PENDIENTE` / `RECHAZADO`), convierte monedas usando tasas
históricas reales (Open Exchange Rates) y analiza un lote de gastos detectando anomalías.

Construido en 3 partes: (1) motor de reglas puro, (2) cliente de tasas de cambio,
(3) analizador de lotes sobre un CSV.

## Arquitectura

Clean Architecture / Hexagonal — el dominio es puro y no conoce la infraestructura:

```
cli  →  infrastructure  →  application  →  domain
                                            (puro, sin I/O)
```

- **domain/**: modelos, reglas (patrón Strategy), resolvedor de prioridades y el motor. Sin red ni archivos.
- **application/**: orquestación y puertos (interfaces) que la infraestructura implementa.
- **infrastructure/**: adaptadores — cliente HTTP de tasas, lector CSV, configuración.
- **cli/**: punto de entrada del analizador de lotes.

> Diseño extensible: agregar una regla nueva = crear una clase en `domain/rules/` y registrarla
> en `registry.py`. El motor y el resolvedor no se tocan (principio Open/Closed).

## Requisitos

- Python 3.12+

## Instalación

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # runtime + herramientas de desarrollo (tests, pyright)
pip install -e .                      # instala el paquete (habilita `python -m expense_engine...`)
```

(Para solo ejecutar, sin dev tools: `pip install -r requirements.txt && pip install -e .`.)

## Configuración (API Key)

El cliente de tasas usa [Open Exchange Rates](https://openexchangerates.org) (plan gratuito).

1. Crea una cuenta y copia tu **App ID**.
2. Copia `.env.example` a `.env.local` y completa el valor:

```bash
cp .env.example .env.local
# edita .env.local:  open_exchange_app_id=TU_APP_ID
```

`.env.local` está en `.gitignore` — la clave nunca se commitea.

## Ejecutar las pruebas

```bash
pytest
```

## Type checking (pyright strict)

```bash
pyright
```

## Ejecutar el analizador de lotes

```bash
python -m expense_engine.cli.analyze "Desafío técnico — Xpendit/gastos_historicos.csv"
```

## Estructura

```
src/expense_engine/   código fuente (domain / application / infrastructure / cli)
tests/                pruebas unitarias
docs/                 documentación de diseño del proyecto
ANALISIS.md           hallazgos del análisis de lotes (Parte 3)
```
