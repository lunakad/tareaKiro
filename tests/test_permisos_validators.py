import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from permisos.validators import validar_permiso

VALID_BASE = {"nombre": "leer", "sistema_id": 1}


def test_datos_validos_sin_errores():
    assert validar_permiso(VALID_BASE) == []


def test_partial_vacio_sin_errores():
    assert validar_permiso({}, partial=True) == []


def test_sistema_id_cero_rechazado():
    data = {**VALID_BASE, "sistema_id": 0}
    assert validar_permiso(data) != []


def test_sistema_id_negativo_rechazado():
    data = {**VALID_BASE, "sistema_id": -1}
    assert validar_permiso(data) != []


@settings(max_examples=100)
@given(nombre=st.just(""))
def test_nombre_vacio_es_rechazado(nombre):
    data = {**VALID_BASE, "nombre": nombre}
    errores = validar_permiso(data)
    assert len(errores) > 0


@settings(max_examples=100)
@given(nombre=st.text(min_size=101, max_size=200))
def test_nombre_demasiado_largo_es_rechazado(nombre):
    data = {**VALID_BASE, "nombre": nombre}
    errores = validar_permiso(data)
    assert len(errores) > 0


@settings(max_examples=100)
@given(descripcion=st.text(min_size=256, max_size=500))
def test_descripcion_demasiado_larga_es_rechazada(descripcion):
    data = {**VALID_BASE, "descripcion": descripcion}
    errores = validar_permiso(data)
    assert len(errores) > 0
