# 06 — Decisiones del Proyecto

Registro de decisiones tomadas con el usuario (Raimundo). Actualizar a medida que se decidan más.

## Stack: Python
- Lenguaje: **Python**. Razón decisiva: el usuario es más fluido en Python y debe poder editar el código EN VIVO frente al entrevistador sin trabarse. Además el analizador de lotes (CSV/finanzas) es idiomático en Python. (Se evaluó TypeScript; descartado solo por fluidez para la etapa en vivo, no por aptitud técnica.)
- Tests: **pytest** (legible, parametrización fácil para cubrir cada regla/estado). [tentativo — confirmar al setup]
- Validación de modelos: **Pydantic** (tipos + validación en runtime, ideal para datos sucios del CSV). [tentativo]
- HTTP: `requests` o `httpx`. [tentativo]
- CSV: módulo `csv` de stdlib (o `pandas` si el análisis lo amerita). [tentativo]
- Tipado: usar type hints en todo el código + **pyright en modo strict** (decisión consciente, 16 jun 2026) para recuperar el chequeo estático equivalente al de TypeScript. Se evaluó TS por su tipado forzado; se mantuvo Python porque (a) los tests —no los tipos— cargan la correctitud de la lógica de negocio, (b) la validación de datos sucios del CSV es runtime y se resuelve con Pydantic (los tipos de TS se borran en runtime igual), y (c) CSV/finanzas es idiomático en Python. El usuario maneja ambos por igual.

## Forma de trabajo: por partes, paso a paso
Implementar Parte 1 → el usuario valida → seguir con Parte 2 → etc. El usuario quiere entender el diseño en detalle para defenderlo en la entrevista. No saltar adelante sin validación.

## Ubicación de documentación y agentes
**Todo dentro del repo**: documentación en `docs/`, agentes del proyecto en `.claude/agents/`. No usar ubicaciones globales para esto. (Decisión explícita del usuario, 16 jun 2026.)

## Pendientes de decidir
- Estructura de carpetas definitiva (`src/`, módulos por parte vs. por capa).
- Cómo se fija "hoy" para el cálculo de antigüedad (fecha de referencia fija vs. runtime).
- Criterio exacto de "duplicado exacto" (con o sin empleado).
- Runner de tests y librerías exactas (confirmar al hacer `npm init`).
