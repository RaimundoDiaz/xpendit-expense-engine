"""Registro de las reglas activas.

Para agregar una regla nueva: créala en este paquete y añádela a `DEFAULT_RULES`.
El motor (`engine.py`) y el resolvedor (`resolver.py`) no necesitan cambiar.
"""

from __future__ import annotations

from expense_engine.domain.rules.age import AgeRule
from expense_engine.domain.rules.base import Rule
from expense_engine.domain.rules.category_limit import CategoryLimitRule
from expense_engine.domain.rules.cost_center import CostCenterRule

DEFAULT_RULES: list[Rule] = [AgeRule(), CategoryLimitRule(), CostCenterRule()]
