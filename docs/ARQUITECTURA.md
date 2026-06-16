# Arquitectura técnica

Documentación para quien lea/mantenga el código. Concisa a propósito; el detalle de
negocio está en `docs/00-overview.md` y siguientes.

## Qué es

Motor que valida gastos contra una política configurable y devuelve un estado
(`APROBADO` / `PENDIENTE` / `RECHAZADO`) con alertas. Se construye en 3 partes:
1. Motor de reglas (lógica pura) — **listo**.
2. Cliente de tasas de cambio (Open Exchange Rates).
3. Analizador de lotes sobre un CSV.

## Capas (Clean Architecture / Hexagonal)

Las dependencias apuntan **hacia adentro**. El dominio no importa nada de afuera.

```
cli  ──▶  infrastructure  ──▶  application  ──▶  domain
(entrada)   (adaptadores)      (orquestación,      (modelos + reglas,
                                define puertos)      sin I/O ni red)
```

| Capa | Responsabilidad | No debe |
|------|-----------------|---------|
| `domain` | Modelos, reglas, resolvedor, motor | Tocar red, archivos, ni librerías de infra |
| `application` | Orquestar; definir **puertos** (interfaces) | Conocer implementaciones concretas |
| `infrastructure` | Adaptadores: HTTP de tasas, lector CSV, config | Contener lógica de negocio |
| `cli` | Punto de entrada | Contener lógica de negocio |

## Flujo de datos (un gasto → un resultado)

```
Expense (moneda original)
   │  normalizer.convert() vía ExchangeRateProvider  [application + infra]
   ▼
NormalizedExpense (monto en USD)
   │  validate_expense(ctx)                           [domain, puro]
   ▼
ValidationResult { expense_id, status, alerts }
   │  model_dump(by_alias=True)
   ▼
JSON con llaves del spec: { gasto_id, status, alertas:[{codigo, mensaje}] }
```

Decisión central: **el motor es puro y recibe el monto YA convertido a USD**
(`NormalizedExpense`). No conoce monedas ni red. La conversión vive en una capa
aparte (Parte 2/3) detrás del puerto `ExchangeRateProvider`. Ver `docs/06-decisiones.md`.

## El patrón de reglas (cómo extender)

Cada regla es una **Strategy**: una clase que cumple el `Protocol` `Rule`
(`domain/rules/base.py`) y devuelve una `PartialEvaluation` o `None` si no aplica.

```python
class Rule(Protocol):
    name: str
    def evaluate(self, ctx: EvaluationContext) -> PartialEvaluation | None: ...
```

El motor (`engine.py`) itera la lista `DEFAULT_RULES` (`rules/registry.py`),
recolecta las evaluaciones y delega en el `resolver` el estado final por prioridad:
**RECHAZADO > PENDIENTE > APROBADO**; si ninguna regla aplica, `PENDIENTE`.

> **Agregar una regla nueva** = crear una clase en `domain/rules/` y añadirla a
> `DEFAULT_RULES`. `engine.py` y `resolver.py` **no se modifican** (principio Open/Closed).

El `EvaluationContext` agrupa todo lo que una regla podría necesitar
(gasto normalizado, empleado, política, `reference_date`), así una regla que
requiera un dato nuevo no cambia la firma de `evaluate`.

## Modelos clave (`domain/models.py`)

- `Expense`, `Employee`, `Policy` — Pydantic; parsean el español del CSV/JSON con
  `validation_alias` (anti-corruption layer).
- `NormalizedExpense` — gasto + `amount_base` (USD), conserva el original.
- `Alert`, `ValidationResult` — serializan al español del spec con `serialization_alias`.
- Dinero en `Decimal`; `Status` es un `Literal` de los 3 estados.

## Convenciones

- **Tipado estricto**: `pyright` en modo `strict`, sin errores. Type hints en todo.
- **Pruebas**: `pytest`; el dominio se prueba sin red ni archivos (monto pre-convertido
  o `MockExchangeRateProvider`).
- **Naming**: identificadores en inglés; los datos externos y el output usan las
  llaves en español vía aliases de Pydantic.
- **Secretos**: la API key va en `.env.local` (gitignored); nunca hardcodeada.
