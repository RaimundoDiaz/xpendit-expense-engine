# Agentes del Proyecto

Los **agentes (subagents) específicos de este proyecto** viven aquí, en `.claude/agents/`, no en una ubicación global. Cada agente es un archivo `.md` con frontmatter (`name`, `description`, `tools`, opcional `model`) seguido del system prompt.

Esto mantiene los agentes versionados junto al repo y disponibles para cualquiera que lo clone.

## Agentes definidos

- **`revisor-de-reglas`** — audita una regla nueva (3 estados, alertas, registro, tests).
- **`guardian-arquitectura`** — verifica los límites hexagonales (dominio puro, deps hacia adentro).
- **`qa-y-pruebas`** — QA del código: corre suite + pyright, detecta huecos y escribe tests.

> Estos agentes (y las skills en `.claude/skills/`) son **trabajo por iniciativa propia**, fuera
> del alcance del desafío. Ver [`docs/08-extras-iniciativa.md`](../../docs/08-extras-iniciativa.md).
