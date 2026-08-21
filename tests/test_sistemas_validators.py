from hypothesis import given, settings
from hypothesis import strategies as st

from sistemas.validators import validar_sistema

VALID_BASE = {"nombre": "ERP"}


@given(nombre=st.just(""))
@settings(max_examples=100)
def test_prop1_nombre_vacio_es_rechazado(nombre):
    errores = validar_sistema({**VALID_BASE, "nombre": nombre})
    assert errores, f"Se esperaban errores para nombre vacío, pero no hubo ninguno."


@given(nombre=st.text(min_size=101, max_size=200))
@settings(max_examples=100)
def test_prop2_nombre_demasiado_largo_es_rechazado(nombre):
    errores = validar_sistema({**VALID_BASE, "nombre": nombre})
    assert errores, f"Se esperaban errores para nombre de longitud {len(nombre)}, pero no hubo ninguno."


@given(descripcion=st.text(min_size=256, max_size=500))
@settings(max_examples=100)
def test_prop3_descripcion_demasiado_larga_es_rechazada(descripcion):
    errores = validar_sistema({**VALID_BASE, "descripcion": descripcion})
    assert errores, f"Se esperaban errores para descripcion de longitud {len(descripcion)}, pero no hubo ninguno."


def test_datos_validos_no_producen_errores():
    errores = validar_sistema(VALID_BASE)
    assert errores == [], f"Errores inesperados con datos válidos: {errores}"


def test_partial_dict_vacio_no_produce_errores():
    errores = validar_sistema({}, partial=True)
    assert errores == [], f"Errores inesperados con partial=True y dict vacío: {errores}"
