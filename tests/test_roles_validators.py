from hypothesis import given, settings
from hypothesis import strategies as st

from roles.validators import validar_rol

VALID_BASE = {"nombre": "Admin"}


@given(nombre=st.just(""))
@settings(max_examples=100)
def test_nombre_vacio_es_rechazado(nombre):
    errores = validar_rol({"nombre": nombre})
    assert errores


@given(nombre=st.text(min_size=51, max_size=200))
@settings(max_examples=100)
def test_nombre_demasiado_largo_es_rechazado(nombre):
    errores = validar_rol({"nombre": nombre})
    assert errores


@given(descripcion=st.text(min_size=256, max_size=500))
@settings(max_examples=100)
def test_descripcion_demasiado_larga_es_rechazada(descripcion):
    data = {**VALID_BASE, "descripcion": descripcion}
    errores = validar_rol(data)
    assert errores


def test_valid_base_no_produce_errores():
    errores = validar_rol(VALID_BASE)
    assert errores == []


def test_partial_sin_nombre_no_produce_errores():
    errores = validar_rol({}, partial=True)
    assert errores == []
