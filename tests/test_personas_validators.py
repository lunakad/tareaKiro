"""
Property-based tests para los validadores de Persona.

Propiedades implementadas (task 2.3):
  - Propiedad 1: Rechazo universal de campos de longitud inválida en Persona
    Valida: Requerimiento 1.7
  - Propiedad 2: Rechazo universal de emails con formato inválido
    Valida: Requerimientos 1.5, 3.6
  - Propiedad 3: Rechazo universal de fechas futuras o malformadas
    Valida: Requerimientos 1.6, 1.8
"""

from datetime import date, timedelta

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from personas.validators import validar_persona

# ---------------------------------------------------------------------------
# Datos base válidos que sirven de punto de partida para las propiedades
# ---------------------------------------------------------------------------

VALID_BASE = {
    "nombre": "Ana",
    "apellido": "García",
    "documento": "12345678",
    "fecha_nacimiento": "1990-06-15",
    "email": "ana@example.com",
}


def _data_with(**kwargs) -> dict:
    """Devuelve VALID_BASE sobreescribiendo los campos dados."""
    d = dict(VALID_BASE)
    d.update(kwargs)
    return d


# ---------------------------------------------------------------------------
# Propiedad 1 — Rechazo universal de campos de longitud inválida en Persona
# Valida: Requerimiento 1.7
# ---------------------------------------------------------------------------

@given(
    nombre=st.one_of(
        st.just(""),                                       # longitud 0
        st.text(min_size=101, max_size=200),               # longitud > 100
    )
)
@settings(max_examples=100)
def test_prop1_nombre_longitud_invalida_es_rechazado(nombre):
    """
    **Validates: Requirements 1.7**
    Un nombre con longitud 0 o > 100 caracteres siempre produce al menos un error.
    """
    errores = validar_persona(_data_with(nombre=nombre))
    assert errores, f"Se esperaban errores para nombre de longitud {len(nombre)!r}, pero no hubo ninguno."


@given(
    apellido=st.one_of(
        st.just(""),
        st.text(min_size=101, max_size=200),
    )
)
@settings(max_examples=100)
def test_prop1_apellido_longitud_invalida_es_rechazado(apellido):
    """
    **Validates: Requirements 1.7**
    Un apellido con longitud 0 o > 100 caracteres siempre produce al menos un error.
    """
    errores = validar_persona(_data_with(apellido=apellido))
    assert errores, f"Se esperaban errores para apellido de longitud {len(apellido)!r}."


@given(
    documento=st.one_of(
        st.just(""),
        st.text(min_size=21, max_size=60),
    )
)
@settings(max_examples=100)
def test_prop1_documento_longitud_invalida_es_rechazado(documento):
    """
    **Validates: Requirements 1.7**
    Un documento con longitud 0 o > 20 caracteres siempre produce al menos un error.
    """
    errores = validar_persona(_data_with(documento=documento))
    assert errores, f"Se esperaban errores para documento de longitud {len(documento)!r}."


# ---------------------------------------------------------------------------
# Propiedad 2 — Rechazo universal de emails con formato inválido
# Valida: Requerimientos 1.5, 3.6
# ---------------------------------------------------------------------------

# Estrategia: texto que no contenga '@' → siempre inválido como email
_email_sin_arroba = st.text(
    alphabet=st.characters(blacklist_characters="@\n\r "),
    min_size=1,
    max_size=80,
).filter(lambda s: "@" not in s)

# Estrategia: texto con más de un '@' o sin dominio completo
_email_malformado = st.one_of(
    _email_sin_arroba,
    # "@dominio.com" — falta la parte local
    st.just("@dominio.com"),
    # "local@" — falta el dominio
    st.just("local@"),
    # "local@dominio" — falta el TLD (sin punto tras el '@')
    st.builds(
        lambda local, domain: f"{local}@{domain}",
        local=st.text(
            alphabet=st.characters(blacklist_characters="@\n\r "),
            min_size=1,
            max_size=30,
        ).filter(lambda s: s),
        domain=st.text(
            alphabet=st.characters(blacklist_characters="@.\n\r "),
            min_size=1,
            max_size=20,
        ).filter(lambda s: s),
    ),
)


@given(email=_email_malformado)
@settings(max_examples=100)
def test_prop2_email_invalido_es_rechazado(email):
    """
    **Validates: Requirements 1.5, 3.6**
    Un email que no cumple el patrón ^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$ siempre produce error.
    """
    errores = validar_persona(_data_with(email=email))
    assert errores, f"Se esperaban errores para email inválido {email!r}, pero no hubo ninguno."


# ---------------------------------------------------------------------------
# Propiedad 3 — Rechazo universal de fechas futuras o malformadas
# Valida: Requerimientos 1.6, 1.8
# ---------------------------------------------------------------------------

# Estrategia: fechas ISO futuras (hoy + 1 día hasta hoy + 1000 días)
_fecha_futura = st.integers(min_value=1, max_value=1000).map(
    lambda delta: (date.today() + timedelta(days=delta)).isoformat()
)

# Estrategia: cadenas que no son fechas ISO válidas
_fecha_malformada = st.one_of(
    st.just("no-es-fecha"),
    st.just("2020/01/01"),
    st.just("01-01-2020"),
    st.just(""),
    st.just("9999-99-99"),
    st.just("2020-13-01"),
    st.just("2020-00-15"),
    st.text(min_size=1, max_size=15).filter(
        lambda s: _es_fecha_invalida(s)
    ),
)


def _es_fecha_invalida(s: str) -> bool:
    """Devuelve True si la cadena NO es una fecha ISO válida."""
    try:
        date.fromisoformat(s)
        return False
    except ValueError:
        return True


@given(fecha=_fecha_futura)
@settings(max_examples=100)
def test_prop3_fecha_futura_es_rechazada(fecha):
    """
    **Validates: Requirements 1.6, 1.8**
    Una fecha de nacimiento en el futuro siempre produce al menos un error.
    """
    errores = validar_persona(_data_with(fecha_nacimiento=fecha))
    assert errores, f"Se esperaban errores para fecha futura {fecha!r}, pero no hubo ninguno."


@given(fecha=_fecha_malformada)
@settings(max_examples=100)
def test_prop3_fecha_malformada_es_rechazada(fecha):
    """
    **Validates: Requirements 1.6, 1.8**
    Una cadena que no es una fecha ISO válida siempre produce al menos un error.
    """
    errores = validar_persona(_data_with(fecha_nacimiento=fecha))
    assert errores, f"Se esperaban errores para fecha malformada {fecha!r}, pero no hubo ninguno."


# ---------------------------------------------------------------------------
# Smoke test — datos completamente válidos no producen errores
# ---------------------------------------------------------------------------

def test_datos_validos_no_producen_errores():
    """Verificación de cordura: VALID_BASE no debe generar ningún error."""
    errores = validar_persona(VALID_BASE)
    assert errores == [], f"Errores inesperados con datos válidos: {errores}"
