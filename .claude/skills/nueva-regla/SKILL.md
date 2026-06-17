---
name: nueva-regla
description: Crea una regla nueva del motor de gastos de Xpendit — genera el archivo de la regla (desde _template.py), su test espejo, la registra en DEFAULT_RULES y corre la suite. Úsala cuando el usuario pida "agregar/crear una regla", "nueva regla de gastos", o describa una condición de validación nueva (límite, prohibición, umbral, moneda, etc.).
---

# Crear una regla nueva del motor de gastos

El motor es data-driven y extensible vía patrón Strategy: cada regla es una clase con
`evaluate(ctx)`. Agregar una regla NO toca `engine.py` ni `resolver.py` (Open/Closed).
Esta skill automatiza los 3 pasos del scaffold ya documentado en
`src/expense_engine/domain/rules/_template.py`.

## 1. Reunir la especificación

Si el usuario no lo dijo, pregúntale (en una sola tanda, con AskUserQuestion si conviene):

- **Qué valida** la regla, en una frase.
- **Cuándo NO aplica** (cuándo devuelve `None`) — p. ej. si la política no define el dato.
- **Los casos y su estado**: qué condición → `APROBADO` / `PENDIENTE` / `RECHAZADO`.
- **¿Necesita datos nuevos en la política?** Si sí, hay que agregar el campo al modelo
  correspondiente en `domain/models.py` (con `validation_alias` en español) y a `policy.json`.
- **Nombre**: deriva `name` en MAYÚSCULAS (p. ej. `LIMITE_MONEDA`) y el archivo en
  snake_case (`currency_limit.py`).

## 2. Crear el archivo de la regla

- Cópialo desde `src/expense_engine/domain/rules/_template.py` a
  `src/expense_engine/domain/rules/<nombre>.py`.
- Renombra la clase (`TemplateRule` → p. ej. `CurrencyLimitRule`) y `name`.
- Implementa `evaluate`: borra el `return None` final inerte y los `_ = ...` que no uses.
- Convenciones obligatorias (ver el template):
  - Devuelve `None` cuando la regla no aplica.
  - `APROBADO` va **sin** alerta; `PENDIENTE` y `RECHAZADO` llevan una `Alert(code=self.name, message=...)`.
  - El monto a comparar contra límites es `ctx.normalized_expense.amount_base` (ya en moneda base).
  - Mensajes de alerta en español, accionables, mismo tono que las reglas existentes
    (`age.py`, `category_limit.py`, `cost_center.py`).

## 3. Crear el test espejo

- Cópialo desde `tests/domain/test__template_rule.py` a
  `tests/domain/test_<nombre>.py`.
- Cambia el import a tu clase y escribe **un test por cada caso** (APROBADO / PENDIENTE /
  RECHAZADO) más el caso "no aplica" (`None`) si corresponde.
- Usa `build_context(...)` de `tests/helpers.py`: cada kwarg tiene default
  (`amount_base`, `category`, `currency`, `expense_date`, `cost_center`, `reference_date`,
  `expense_id`, `policy`), así que solo pasas lo que el caso necesita.
- Si la regla lee un campo nuevo de la política, agrégalo a `POLICY_DATA` en `helpers.py`
  o construye una `Policy` ad-hoc y pásala con `policy=...`.

## 4. Registrar la regla

Edita `src/expense_engine/domain/rules/registry.py`: importa la clase y agrégala a
`DEFAULT_RULES`. Recuerda la tabla de prioridades del resolver: un solo `RECHAZADO`
de cualquier regla manda; ordenar la lista no cambia el resultado final, pero sí el
orden de las alertas en el resultado.

## 5. Verificar

Corre `python -m pytest -q` y confirma que toda la suite pasa (incluidos los tests
nuevos). Si el proyecto usa pyright, corre el type-check también. Reporta el resultado.

## Referencias del repo
- Plantilla: `src/expense_engine/domain/rules/_template.py`
- Reglas reales: `age.py`, `category_limit.py`, `cost_center.py` (mismo paquete)
- Contratos: `domain/rules/base.py` (`Rule`, `EvaluationContext`, `PartialEvaluation`)
- Resolver/motor: `domain/resolver.py`, `domain/engine.py` (NO se modifican)
- Modelos/política: `domain/models.py`, `policy.json`
- Helpers de test: `tests/helpers.py`
