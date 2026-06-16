# 00 — Overview del Desafío

Desafío técnico para el rol de **Software Engineer** en **Xpendit** (evaluador: Nicolás). Tarea asíncrona "para la casa". Si es exitosa, sigue una **entrevista en vivo (~40-60 min)** donde **evolucionarán/escalarán el código entregado** — por eso el diseño y la extensibilidad pesan tanto como la correctitud.

## Qué es Xpendit
Plataforma SaaS que automatiza la gestión de gastos empresariales (expense management). Su funcionalidad core es el **Motor de Reglas de Gastos**: las empresas definen políticas (ej. "Ventas no puede gastar más de $80 USD en cenas") y el motor las aplica automáticamente a cada gasto reportado. Construimos un prototipo de ese motor.

## Glosario clave
- **Gasto (Expense)**: compra/pago que un empleado hace por la empresa y reporta para reembolso.
- **Política (Policy)**: conjunto de reglas que controla cómo se gasta el dinero.
- **Categoría**: en qué se gastó (food, transport, software, lodging, other).
- **Centro de Costo (Cost Center)**: quién/qué área gastó (sales_team, core_engineering, marketing, finance).
- **Estados**: APROBADO (cumple todo, listo a pagar), PENDIENTE (revisión humana de un manager), RECHAZADO (incumple regla, no se reembolsa).
- **Flujo de Aprobación**: proceso que se activa cuando un gasto queda PENDIENTE (secuencia de aprobadores). No es parte obligatoria del prototipo, pero es contexto útil para la entrevista en vivo sobre cómo escalar.

## Plazo y entrega
- Recibido: 16 jun 2026, 14:57 (Chile). **Entrega: martes 23 jun 2026, 14:57 (Chile)** — 5 días hábiles.
- Entregar link a repo Git (o .zip) respondiendo el correo a Nicolás.

## Stack permitido
Python o JavaScript/TypeScript, cualquier framework/librería. **Elegido: TypeScript** (ver `06-decisiones.md`).

## IA
Permitida y **fomentada explícitamente** (ChatGPT, Copilot, etc.). Xpendit valora modelar/pensamiento crítico/uso de herramientas por sobre memorizar.

## Criterios de evaluación
Correctitud + diseño de software + separación de responsabilidades + calidad de pruebas + buen manejo de errores y secretos.

## Las 3 partes
1. Núcleo de lógica pura — el validador (`01-parte1-rules-engine.md`).
2. Integración con API externa de tasas de cambio (`02-parte2-exchange-api.md`).
3. Script de análisis de lotes sobre CSV (`03-parte3-batch-analyzer.md`).
