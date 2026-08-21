from datetime import date

from hypothesis import given, settings, strategies as st

from app import create_app, db as _db


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

alpha = st.characters(whitelist_categories=("Lu", "Ll"))
digits = st.characters(whitelist_categories=("Nd",))

nombres_st = st.text(min_size=1, max_size=50, alphabet=alpha)
documentos_st = st.text(min_size=1, max_size=20, alphabet=digits)
emails_local_st = st.text(min_size=1, max_size=20, alphabet=alpha)
emails_domain_st = st.text(min_size=1, max_size=20, alphabet=alpha)
fechas_st = st.dates(max_value=date.today()).map(lambda d: d.isoformat())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    return app


def _persona_payload(nombre, apellido, documento, email_local, email_domain, fecha):
    return {
        "nombre": nombre,
        "apellido": apellido,
        "documento": documento,
        "fecha_nacimiento": fecha,
        "email": f"{email_local}@{email_domain}.com",
    }


# ---------------------------------------------------------------------------
# Propiedad 4: Unicidad de documento y email en creación de Persona
# Valida: Requerimientos 1.2, 1.3, 9.5
# ---------------------------------------------------------------------------

@given(
    nombre=nombres_st,
    apellido=nombres_st,
    documento=documentos_st,
    email_local=emails_local_st,
    email_domain=emails_domain_st,
    fecha=fechas_st,
)
@settings(max_examples=50)
def test_property_4_unicidad_documento_email(
    nombre, apellido, documento, email_local, email_domain, fecha
):
    """**Validates: Requirements 1.2, 1.3, 9.5**"""
    app = _make_app()
    with app.app_context():
        _db.create_all()
        client = app.test_client()

        payload = _persona_payload(nombre, apellido, documento, email_local, email_domain, fecha)

        resp1 = client.post("/personas", json=payload)
        assert resp1.status_code == 201

        # Same documento, different email
        payload_dup_doc = {**payload, "email": f"x{email_local}@other.com"}
        resp2 = client.post("/personas", json=payload_dup_doc)
        assert resp2.status_code == 409

        # Same email, different documento
        new_doc = (documento + "0")[:20]
        payload_dup_email = {**payload, "documento": new_doc}
        resp3 = client.post("/personas", json=payload_dup_email)
        assert resp3.status_code == 409

        _db.session.remove()
        _db.drop_all()


# ---------------------------------------------------------------------------
# Propiedad 5: Round-trip creación/consulta de Persona
# Valida: Requerimientos 1.1, 2.3
# ---------------------------------------------------------------------------

@given(
    nombre=nombres_st,
    apellido=nombres_st,
    documento=documentos_st,
    email_local=emails_local_st,
    email_domain=emails_domain_st,
    fecha=fechas_st,
)
@settings(max_examples=50)
def test_property_5_round_trip_persona(
    nombre, apellido, documento, email_local, email_domain, fecha
):
    """**Validates: Requirements 1.1, 2.3**"""
    app = _make_app()
    with app.app_context():
        _db.create_all()
        client = app.test_client()

        payload = _persona_payload(nombre, apellido, documento, email_local, email_domain, fecha)

        resp_create = client.post("/personas", json=payload)
        assert resp_create.status_code == 201
        created = resp_create.get_json()
        persona_id = created["id"]

        resp_get = client.get(f"/personas/{persona_id}")
        assert resp_get.status_code == 200
        fetched = resp_get.get_json()

        assert fetched["nombre"] == nombre
        assert fetched["apellido"] == apellido
        assert fetched["documento"] == documento
        assert fetched["email"] == f"{email_local}@{email_domain}.com"
        assert fetched["fecha_nacimiento"] == fecha

        _db.session.remove()
        _db.drop_all()


# ---------------------------------------------------------------------------
# Propiedad 6: Listado solo incluye registros activos
# Valida: Requerimientos 2.1, 2.2
# ---------------------------------------------------------------------------

@given(
    nombre=nombres_st,
    apellido=nombres_st,
    documento=documentos_st,
    email_local=emails_local_st,
    email_domain=emails_domain_st,
    fecha=fechas_st,
)
@settings(max_examples=50)
def test_property_6_listado_solo_activos(
    nombre, apellido, documento, email_local, email_domain, fecha
):
    """**Validates: Requirements 2.1, 2.2**"""
    app = _make_app()
    with app.app_context():
        _db.create_all()
        client = app.test_client()

        payload = _persona_payload(nombre, apellido, documento, email_local, email_domain, fecha)

        resp_create = client.post("/personas", json=payload)
        assert resp_create.status_code == 201
        created = resp_create.get_json()
        assert created["activo"] is True

        resp_list = client.get("/personas")
        assert resp_list.status_code == 200
        personas = resp_list.get_json()

        for p in personas:
            assert p["activo"] is True

        ids = [p["id"] for p in personas]
        assert created["id"] in ids

        _db.session.remove()
        _db.drop_all()


# ---------------------------------------------------------------------------
# Propiedad 7: Actualización parcial preserva campos no provistos
# Valida: Requerimiento 3.1
# ---------------------------------------------------------------------------

@given(
    nombre=nombres_st,
    apellido=nombres_st,
    documento=documentos_st,
    email_local=emails_local_st,
    email_domain=emails_domain_st,
    fecha=fechas_st,
    nuevo_nombre=nombres_st,
)
@settings(max_examples=50)
def test_property_7_actualizacion_parcial_preserva_campos(
    nombre, apellido, documento, email_local, email_domain, fecha, nuevo_nombre
):
    """**Validates: Requirements 3.1**"""
    app = _make_app()
    with app.app_context():
        _db.create_all()
        client = app.test_client()

        payload = _persona_payload(nombre, apellido, documento, email_local, email_domain, fecha)

        resp_create = client.post("/personas", json=payload)
        assert resp_create.status_code == 201
        created = resp_create.get_json()
        persona_id = created["id"]

        resp_put = client.put(f"/personas/{persona_id}", json={"nombre": nuevo_nombre})
        assert resp_put.status_code == 200
        updated = resp_put.get_json()

        assert updated["nombre"] == nuevo_nombre
        assert updated["apellido"] == apellido
        assert updated["documento"] == documento
        assert updated["email"] == f"{email_local}@{email_domain}.com"
        assert updated["fecha_nacimiento"] == fecha

        _db.session.remove()
        _db.drop_all()


# ---------------------------------------------------------------------------
# Propiedad 8: Integridad referencial en eliminación de Persona con Usuarios
# Valida: Requerimiento 4.3
# ---------------------------------------------------------------------------

@given(
    nombre=nombres_st,
    apellido=nombres_st,
    documento=documentos_st,
    email_local=emails_local_st,
    email_domain=emails_domain_st,
    fecha=fechas_st,
    username=st.text(min_size=3, max_size=30, alphabet=alpha),
)
@settings(max_examples=10, deadline=None)
def test_property_8_integridad_referencial_persona_con_usuario(
    nombre, apellido, documento, email_local, email_domain, fecha, username
):
    """**Validates: Requirements 4.3**"""
    app = _make_app()
    with app.app_context():
        _db.create_all()
        client = app.test_client()

        payload = _persona_payload(nombre, apellido, documento, email_local, email_domain, fecha)

        resp_persona = client.post("/personas", json=payload)
        assert resp_persona.status_code == 201
        persona_id = resp_persona.get_json()["id"]

        resp_usuario = client.post("/usuarios", json={
            "persona_id": persona_id,
            "username": username,
            "password": "Secreto123",
        })
        assert resp_usuario.status_code == 201

        resp_delete = client.delete(f"/personas/{persona_id}")
        assert resp_delete.status_code == 409

        resp_get = client.get(f"/personas/{persona_id}")
        assert resp_get.status_code == 200

        _db.session.remove()
        _db.drop_all()
