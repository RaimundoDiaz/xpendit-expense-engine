"""PLANTILLA de tests para una regla nueva — copia junto con `_template.py`.

Cómo usar:
  1. Copia este archivo a `test_mi_regla.py` y cambia el import a tu clase.
  2. Escribe un test por cada CASO de la regla (APROBADO / PENDIENTE / RECHAZADO)
     y uno para el caso "no aplica" (devuelve None), si corresponde.
  3. Usa `build_context(...)` para armar el escenario; cada kwarg tiene default,
     así que solo pasas lo que tu caso necesita (ver `tests/helpers.py`).

El template es inerte (siempre None), así que su único test verifica eso. Reemplaza
estos tests por los reales al implementar tu regla.
"""

from __future__ import annotations

from expense_engine.domain.rules._template import TemplateRule
from tests.helpers import build_context


def test_template_does_not_apply_by_default() -> None:
    # El template inerte no opina sobre ningún gasto.
    assert TemplateRule().evaluate(build_context()) is None


# Esqueletos a rellenar cuando implementes tu regla (descoméntalos y ajústalos):
#
# def test_caso_aprobado() -> None:
#     result = MiRegla().evaluate(build_context(amount_base="50", category="food"))
#     assert result is not None
#     assert result.status == "APROBADO"
#     assert result.alert is None  # APROBADO no lleva alerta
#
# def test_caso_pendiente() -> None:
#     result = MiRegla().evaluate(build_context(amount_base="120", category="food"))
#     assert result is not None
#     assert result.status == "PENDIENTE"
#     assert result.alert is not None
#     assert result.alert.code == "MI_REGLA"
#
# def test_caso_rechazado() -> None:
#     result = MiRegla().evaluate(build_context(amount_base="999", category="food"))
#     assert result is not None
#     assert result.status == "RECHAZADO"
