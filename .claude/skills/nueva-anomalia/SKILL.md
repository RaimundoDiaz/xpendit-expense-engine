---
name: nueva-anomalia
description: Agrega un detector de anomalías nuevo al analizador de lotes del motor de gastos de Xpendit (p. ej. outliers, montos sospechosos, gastos en fin de semana, duplicados por empleado) con su test. Úsala cuando el usuario pida "detectar X en el lote", "agregar una anomalía", o describa un patrón sospechoso a marcar.
---

# Agregar un detector de anomalías

Las anomalías viven en `application/anomalies.py` (hoy: duplicados exactos y montos negativos)
y se invocan desde `batch_analyzer.analyze`, que las agrega en `BatchReport`. Un detector es
una función pura sobre la secuencia de `Expense` (o de registros, si necesita el empleado).

## 1. Reunir la especificación
- **Qué patrón** se detecta y por qué es sospechoso, en una frase.
- **Qué devuelve:** ¿una lista de gastos? ¿grupos (como `DuplicateGroup`)? ¿gastos con un
  score? Define un `@dataclass(frozen=True)` para el resultado si no es una lista plana.
- **Qué datos necesita:** solo el gasto (`Expense`) o también el empleado (`ExpenseRecord` /
  el monto normalizado). Elige la firma mínima.
- **Parámetros/umbral:** ¿es fijo o configurable? Si es configurable, considera pasarlo como
  argumento de la función (no lo escondas como constante).

## 2. Implementar el detector
- En `application/anomalies.py`, una función `find_<algo>(expenses: Sequence[Expense]) -> ...`
  pura (sin I/O), siguiendo el estilo de `find_exact_duplicates` / `find_negative_amounts`.
- Si necesita el empleado, recibe `Sequence[ExpenseRecord]` en su lugar.
- Docstring en español explicando el criterio exacto (p. ej. "duplicados del mismo empleado").

## 3. Cablear en el reporte
- Agrega un campo al `@dataclass BatchReport` en `batch_analyzer.py`.
- En `analyze(...)`, llama al detector y rellena el campo nuevo.
- Si quieres que el CLI lo muestre, agrega su sección en `_print_report` (`cli/analyze.py`).

> **Nota de escala (opcional):** si el set de anomalías crece, conviene migrar a un *registry*
> de detectores (un `Protocol` + lista, espejo de `domain/rules/registry.py`). Documentado como
> seam en `docs/07-escalabilidad.md` §6. Para 1–2 detectores, la función directa es suficiente.

## 4. Crear el test
- En `tests/application/test_anomalies.py` (o un archivo nuevo si el detector es grande).
- Construye `Expense` directamente (campos en inglés: `id`, `amount`, `currency`, `date`,
  `category`) o usa los helpers. Cubre: caso que detecta, caso limpio (lista vacía), y bordes.

## 5. Verificar
`python -m pytest -q` y `pyright`. Reporta el resultado.

## Referencias del repo
- Detectores actuales: `application/anomalies.py` (`find_exact_duplicates`, `find_negative_amounts`)
- Agregación: `application/batch_analyzer.py` (`BatchReport`, `analyze`)
- Salida CLI: `cli/analyze.py` (`_print_report`)
- Modelo: `domain/models.py` (`Expense`, `ExpenseRecord`)
- Tests: `tests/application/test_anomalies.py`
