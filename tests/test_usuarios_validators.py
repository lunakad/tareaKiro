"""
Property-based tests para los validadores de Usuario.

Propiedades implementadas (task 4.3):
  - Propiedad 11: Rechazo universal de contraseñas fuera de rango (< 8 o > 128 chars)
    Valida: Requerimientos 5.6, 7.4
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from usuarios.validators import validar_usuario

# ---------------------------------------------------------------------------
# Datos base válidos que sirven de punto de partida para las propiedades
# ---------------------------------------------------------------------------

VALID_BASE = {
    "persona_id": 1,
    "username": "usuario_test",
    "password": "Passw0rd!",
}


def _data_with(**kwargs) -> dict:
    """Devuelve VALID_BASE sobreescribiendo los campos dados."""
    d = dict(VALID_BASE)
    d.update(kwargs)
    return d


# ---------------------------------------------------------------------------
# Propiedad 11 — Rechazo universal de contraseñas fuera de rango
# Valida: Requerimientos 5.6, 7.4
# ---------------------------------------------------------------------------

@given(
    password=st.text(min_size=1, max_size=7)
)
@settings(max_examples=100)
def test_prop11_password_demasiado_corto_es_rechazado(password):
    """
    **Validates: Requirements 5.6, 7.4**
    Una contraseña con menos de 8 caracteres siempre produce al menos un error.
    """
    errores = validar_usuario(_data_with(password=password))
    assert errores, (
        f"Se esperaban errores para password de longitud {len(password)!r} "
        f"(< 8), pero no hubo ninguno."
    )


@given(
    password=st.text(min_size=129, max_size=200)
)
@settings(max_examples=100)
def test_prop11_password_demasiado_largo_es_rechazado(password):
    """
    **Validates: Requirements 5.6, 7.4**
    Una contraseña con más de 128 caracteres siempre produce al menos un error.
    """
    errores = validar_usuario(_data_with(password=password))
    assert errores, (
        f"Se esperaban errores para password de longitud {len(password)!r} "
        f"(> 128), pero no hubo ninguno."
    )


# ---------------------------------------------------------------------------
# Smoke test — contraseña válida (8–128 chars) no produce error de password
# ---------------------------------------------------------------------------

@given(
    password=st.text(min_size=8, max_size=128)
)
@settings(max_examples=100)
def test_prop11_password_en_rango_no_produce_error_de_password(password):
    """
    **Validates: Requirements 5.6, 7.4**
    Una contraseña dentro del rango 8–128 no genera errores relacionados con 'password'.
    """
    errores = validar_usuario(_data_with(password=password))
    errores_password = [e for e in errores if "password" in e.lower()]
    assert not errores_password, (
        f"No se esperaban errores de password para longitud {len(password)!r}, "
        f"pero se obtuvieron: {errores_password}"
    )
