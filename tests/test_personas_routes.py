"""
Tests de rutas REST para el recurso Persona.

Cubre todos los flujos de éxito y error de los endpoints:
    POST   /personas          → 201, 400, 409
    GET    /personas          → 200
    GET    /personas/<id>     → 200, 404, 422
    PUT    /personas/<id>     → 200, 400, 404, 409
    DELETE /personas/<id>     → 204, 404, 409, 422

Requerimientos: 1.1–1.8, 2.1–2.5, 3.1–3.6, 4.1–4.4
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def post_persona(client, data):
    """Envía POST /personas y devuelve la respuesta."""
    return client.post("/personas", json=data)


def create_persona(client, data):
    """Crea una Persona y devuelve el JSON del objeto creado (201)."""
    resp = post_persona(client, data)
    assert resp.status_code == 201, f"No se pudo crear la Persona: {resp.get_json()}"
    return resp.get_json()


def create_usuario(client, persona_id, username="juanperez", password="Secreto123"):
    """Crea un Usuario asociado a persona_id y devuelve el JSON (201)."""
    resp = client.post("/usuarios", json={
        "persona_id": persona_id,
        "username": username,
        "password": password,
    })
    assert resp.status_code == 201, f"No se pudo crear el Usuario: {resp.get_json()}"
    return resp.get_json()


# ===========================================================================
# POST /personas
# ===========================================================================

class TestCrearPersona:
    """POST /personas"""

    def test_creacion_exitosa_devuelve_201(self, client, persona_data):
        """Req 1.1: Creación válida devuelve 201 con todos los campos."""
        resp = post_persona(client, persona_data)
        assert resp.status_code == 201

    def test_respuesta_contiene_todos_los_campos(self, client, persona_data):
        """Req 1.1: El objeto retornado tiene id, nombre, apellido, documento,
        fecha_nacimiento, email, activo, created_at, updated_at."""
        resp = post_persona(client, persona_data)
        body = resp.get_json()
        for campo in ("id", "nombre", "apellido", "documento",
                      "fecha_nacimiento", "email", "activo",
                      "created_at", "updated_at"):
            assert campo in body, f"Campo '{campo}' ausente en la respuesta"

    def test_respuesta_no_contiene_datos_sensibles(self, client, persona_data):
        """La respuesta no debe contener campos sensibles como password_hash."""
        resp = post_persona(client, persona_data)
        body = resp.get_json()
        assert "password" not in body
        assert "password_hash" not in body

    def test_respuesta_refleja_datos_enviados(self, client, persona_data):
        """Los valores del objeto retornado coinciden con los enviados."""
        resp = post_persona(client, persona_data)
        body = resp.get_json()
        assert body["nombre"] == persona_data["nombre"]
        assert body["apellido"] == persona_data["apellido"]
        assert body["documento"] == persona_data["documento"]
        assert body["fecha_nacimiento"] == persona_data["fecha_nacimiento"]
        assert body["email"] == persona_data["email"]

    # --- 400: campos obligatorios faltantes ---

    @pytest.mark.parametrize("campo_faltante", [
        "nombre", "apellido", "documento", "fecha_nacimiento", "email"
    ])
    def test_400_campo_obligatorio_faltante(self, client, persona_data, campo_faltante):
        """Req 1.4: Falta un campo obligatorio → 400."""
        data = {k: v for k, v in persona_data.items() if k != campo_faltante}
        resp = post_persona(client, data)
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body

    # --- 400: formato de email inválido ---

    @pytest.mark.parametrize("email_invalido", [
        "noesunmail",
        "falta_arroba.com",
        "@sinlocal.com",
        "local@",
        "local@sin_tld",
        "dos@@arrobas.com",
    ])
    def test_400_email_formato_invalido(self, client, persona_data, email_invalido):
        """Req 1.5: Email con formato inválido → 400."""
        data = {**persona_data, "email": email_invalido}
        resp = post_persona(client, data)
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body

    # --- 400: formato de fecha inválido ---

    @pytest.mark.parametrize("fecha_invalida", [
        "01-06-1990",    # formato DD-MM-YYYY
        "1990/06/15",    # separador incorrecto
        "no-es-fecha",   # texto libre
        "9999-99-99",    # fecha imposible
        "",              # vacío
    ])
    def test_400_fecha_formato_invalido(self, client, persona_data, fecha_invalida):
        """Req 1.6: Fecha con formato distinto a YYYY-MM-DD → 400."""
        data = {**persona_data, "fecha_nacimiento": fecha_invalida}
        resp = post_persona(client, data)
        assert resp.status_code == 400

    def test_400_fecha_futura(self, client, persona_data):
        """Req 1.8: Fecha de nacimiento futura → 400."""
        data = {**persona_data, "fecha_nacimiento": "2099-01-01"}
        resp = post_persona(client, data)
        assert resp.status_code == 400

    def test_400_nombre_demasiado_largo(self, client, persona_data):
        """Req 1.7: Nombre con más de 100 caracteres → 400."""
        data = {**persona_data, "nombre": "A" * 101}
        resp = post_persona(client, data)
        assert resp.status_code == 400

    def test_400_apellido_demasiado_largo(self, client, persona_data):
        """Req 1.7: Apellido con más de 100 caracteres → 400."""
        data = {**persona_data, "apellido": "B" * 101}
        resp = post_persona(client, data)
        assert resp.status_code == 400

    def test_400_documento_demasiado_largo(self, client, persona_data):
        """Req 1.7: Documento con más de 20 caracteres → 400."""
        data = {**persona_data, "documento": "D" * 21}
        resp = post_persona(client, data)
        assert resp.status_code == 400

    # --- 409: duplicados ---

    def test_409_documento_duplicado(self, client, persona_data):
        """Req 1.2: Segundo POST con mismo documento → 409."""
        create_persona(client, persona_data)
        # Segundo intento: mismo documento, email diferente
        data2 = {**persona_data, "email": "otro@example.com"}
        resp = post_persona(client, data2)
        assert resp.status_code == 409
        body = resp.get_json()
        assert "error" in body

    def test_409_email_duplicado(self, client, persona_data):
        """Req 1.3: Segundo POST con mismo email → 409."""
        create_persona(client, persona_data)
        # Segundo intento: mismo email, documento diferente
        data2 = {**persona_data, "documento": "99999999"}
        resp = post_persona(client, data2)
        assert resp.status_code == 409
        body = resp.get_json()
        assert "error" in body


# ===========================================================================
# GET /personas
# ===========================================================================

class TestListarPersonas:
    """GET /personas"""

    def test_200_lista_vacia_si_no_hay_personas(self, client):
        """Req 2.2: Sin personas registradas devuelve [] con 200."""
        resp = client.get("/personas")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_200_lista_con_personas(self, client, persona_data):
        """Req 2.1: Con personas registradas devuelve lista no vacía con 200."""
        create_persona(client, persona_data)
        resp = client.get("/personas")
        assert resp.status_code == 200
        body = resp.get_json()
        assert isinstance(body, list)
        assert len(body) >= 1

    def test_solo_devuelve_personas_activas(self, client, persona_data):
        """Req 2.1, 2.2: GET /personas solo incluye registros con activo=True."""
        create_persona(client, persona_data)
        resp = client.get("/personas")
        assert resp.status_code == 200
        personas = resp.get_json()
        for p in personas:
            assert p["activo"] is True, (
                f"Se encontró una Persona con activo=False en el listado: {p}"
            )

    def test_persona_recien_creada_aparece_en_listado(self, client, persona_data):
        """Tras crear una Persona, aparece en el GET /personas."""
        creada = create_persona(client, persona_data)
        resp = client.get("/personas")
        ids = [p["id"] for p in resp.get_json()]
        assert creada["id"] in ids


# ===========================================================================
# GET /personas/<id>
# ===========================================================================

class TestObtenerPersona:
    """GET /personas/<id>"""

    def test_200_persona_existente(self, client, persona_data):
        """Req 2.3: GET /personas/<id> con id existente devuelve 200."""
        creada = create_persona(client, persona_data)
        resp = client.get(f"/personas/{creada['id']}")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["id"] == creada["id"]
        assert body["nombre"] == persona_data["nombre"]

    def test_200_datos_completos_en_respuesta(self, client, persona_data):
        """La respuesta de GET contiene todos los campos esperados."""
        creada = create_persona(client, persona_data)
        resp = client.get(f"/personas/{creada['id']}")
        body = resp.get_json()
        for campo in ("id", "nombre", "apellido", "documento",
                      "fecha_nacimiento", "email", "activo",
                      "created_at", "updated_at"):
            assert campo in body

    def test_404_id_inexistente(self, client):
        """Req 2.4: GET /personas/9999 devuelve 404."""
        resp = client.get("/personas/9999")
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body

    def test_422_id_no_entero(self, client):
        """Req 2.5: GET /personas/abc devuelve 422."""
        resp = client.get("/personas/abc")
        assert resp.status_code == 422
        body = resp.get_json()
        assert "error" in body

    def test_422_id_cero(self, client):
        """Req 2.5: GET /personas/0 devuelve 422 (no es entero positivo)."""
        resp = client.get("/personas/0")
        assert resp.status_code == 422

    def test_422_id_negativo(self, client):
        """Req 2.5: GET /personas/-1 devuelve 422."""
        resp = client.get("/personas/-1")
        assert resp.status_code == 422


# ===========================================================================
# PUT /personas/<id>
# ===========================================================================

class TestActualizarPersona:
    """PUT /personas/<id>"""

    def test_200_actualizacion_parcial_solo_nombre(self, client, persona_data):
        """Req 3.1: PUT con solo nombre actualiza ese campo y preserva los demás."""
        creada = create_persona(client, persona_data)
        nuevo_nombre = "Carlos"
        resp = client.put(f"/personas/{creada['id']}", json={"nombre": nuevo_nombre})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["nombre"] == nuevo_nombre
        # Los demás campos se preservan
        assert body["apellido"] == persona_data["apellido"]
        assert body["documento"] == persona_data["documento"]
        assert body["email"] == persona_data["email"]
        assert body["fecha_nacimiento"] == persona_data["fecha_nacimiento"]

    def test_200_actualizacion_partial_preserva_campos_no_enviados(self, client, persona_data):
        """Req 3.1: Solo los campos provistos cambian; los omitidos conservan su valor."""
        creada = create_persona(client, persona_data)
        resp = client.put(f"/personas/{creada['id']}", json={"email": "nuevo@example.com"})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["email"] == "nuevo@example.com"
        assert body["nombre"] == persona_data["nombre"]
        assert body["apellido"] == persona_data["apellido"]

    def test_400_cuerpo_vacio(self, client, persona_data):
        """Req 3.2: PUT con cuerpo vacío → 400."""
        creada = create_persona(client, persona_data)
        resp = client.put(f"/personas/{creada['id']}", json={})
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body

    def test_400_sin_campos_modificables(self, client, persona_data):
        """Req 3.2: PUT con campos no reconocidos → 400."""
        creada = create_persona(client, persona_data)
        resp = client.put(f"/personas/{creada['id']}", json={"campo_inexistente": "valor"})
        assert resp.status_code == 400

    def test_404_id_inexistente(self, client):
        """Req 3.3: PUT a id que no existe → 404."""
        resp = client.put("/personas/9999", json={"nombre": "Nuevo"})
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body

    def test_409_documento_duplicado_en_actualizacion(self, client, persona_data):
        """Req 3.4: PUT con documento que ya pertenece a otra Persona → 409."""
        # Crear primera persona
        create_persona(client, persona_data)
        # Crear segunda persona con documento distinto
        data2 = {**persona_data, "documento": "99999999", "email": "otro@example.com"}
        segunda = create_persona(client, data2)
        # Intentar actualizar la segunda con el documento de la primera
        resp = client.put(
            f"/personas/{segunda['id']}",
            json={"documento": persona_data["documento"]}
        )
        assert resp.status_code == 409
        body = resp.get_json()
        assert "error" in body

    def test_409_email_duplicado_en_actualizacion(self, client, persona_data):
        """Req 3.5: PUT con email que ya pertenece a otra Persona → 409."""
        # Crear primera persona
        create_persona(client, persona_data)
        # Crear segunda persona con email distinto
        data2 = {**persona_data, "documento": "99999999", "email": "otro@example.com"}
        segunda = create_persona(client, data2)
        # Intentar actualizar la segunda con el email de la primera
        resp = client.put(
            f"/personas/{segunda['id']}",
            json={"email": persona_data["email"]}
        )
        assert resp.status_code == 409
        body = resp.get_json()
        assert "error" in body

    def test_400_email_invalido_en_actualizacion(self, client, persona_data):
        """Req 3.6: PUT con email de formato inválido → 400."""
        creada = create_persona(client, persona_data)
        resp = client.put(f"/personas/{creada['id']}", json={"email": "no-es-email"})
        assert resp.status_code == 400


# ===========================================================================
# DELETE /personas/<id>
# ===========================================================================

class TestEliminarPersona:
    """DELETE /personas/<id>"""

    def test_204_eliminacion_exitosa(self, client, persona_data):
        """Req 4.1: DELETE de persona sin usuarios asociados → 204 sin cuerpo."""
        creada = create_persona(client, persona_data)
        resp = client.delete(f"/personas/{creada['id']}")
        assert resp.status_code == 204
        assert resp.data == b""

    def test_204_persona_eliminada_no_aparece_en_listado(self, client, persona_data):
        """Req 4.1: Tras DELETE exitoso la persona ya no aparece en GET /personas."""
        creada = create_persona(client, persona_data)
        client.delete(f"/personas/{creada['id']}")
        resp = client.get("/personas")
        ids = [p["id"] for p in resp.get_json()]
        assert creada["id"] not in ids

    def test_204_persona_eliminada_devuelve_404_en_get(self, client, persona_data):
        """Req 4.1: Tras DELETE exitoso, GET /personas/<id> devuelve 404."""
        creada = create_persona(client, persona_data)
        client.delete(f"/personas/{creada['id']}")
        resp = client.get(f"/personas/{creada['id']}")
        assert resp.status_code == 404

    def test_404_id_inexistente(self, client):
        """Req 4.2: DELETE de id que no existe → 404."""
        resp = client.delete("/personas/9999")
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body

    def test_409_persona_con_usuario_asociado(self, client, persona_data):
        """
        Req 4.3: Escenario completo:
          1. Crear Persona → 201
          2. Crear Usuario asociado a esa Persona → 201
          3. Intentar DELETE de la Persona → 409 (tiene usuario)
        """
        # 1. Crear persona
        persona = create_persona(client, persona_data)
        # 2. Crear usuario asociado
        create_usuario(client, persona["id"])
        # 3. Intentar eliminar la persona → debe ser rechazado
        resp = client.delete(f"/personas/{persona['id']}")
        assert resp.status_code == 409
        body = resp.get_json()
        assert "error" in body

    def test_409_persona_no_se_elimina_cuando_tiene_usuario(self, client, persona_data):
        """Req 4.3: La persona sigue existiendo después del 409 en DELETE."""
        persona = create_persona(client, persona_data)
        create_usuario(client, persona["id"])
        # Intentar eliminar
        client.delete(f"/personas/{persona['id']}")
        # Verificar que la persona aún existe
        resp = client.get(f"/personas/{persona['id']}")
        assert resp.status_code == 200

    def test_422_id_no_entero(self, client):
        """Req 4.4: DELETE /personas/abc devuelve 422."""
        resp = client.delete("/personas/abc")
        assert resp.status_code == 422
        body = resp.get_json()
        assert "error" in body

    def test_422_id_cero(self, client):
        """Req 4.4: DELETE /personas/0 devuelve 422."""
        resp = client.delete("/personas/0")
        assert resp.status_code == 422

    def test_422_id_negativo(self, client):
        """Req 4.4: DELETE /personas/-5 devuelve 422."""
        resp = client.delete("/personas/-5")
        assert resp.status_code == 422
