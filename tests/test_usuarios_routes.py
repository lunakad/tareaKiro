"""
Tests de rutas para el recurso Usuario.

Cubre todos los endpoints de /usuarios con flujos de éxito y de error:
    POST   /usuarios          → 201, 400, 404, 409
    GET    /usuarios          → 200
    GET    /usuarios/<id>     → 200, 404, 422
    PUT    /usuarios/<id>     → 200, 400, 404, 409
    DELETE /usuarios/<id>     → 204, 400, 404

Requerimientos: 5.1–5.8, 6.1–6.6, 7.1–7.6, 8.1–8.3
"""

import json
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def crear_persona(client, persona_data):
    """Crea una persona via POST /personas y devuelve el JSON de respuesta."""
    resp = client.post(
        "/personas",
        data=json.dumps(persona_data),
        content_type="application/json",
    )
    assert resp.status_code == 201, (
        f"No se pudo crear la persona de apoyo: {resp.get_json()}"
    )
    return resp.get_json()


def crear_usuario(client, usuario_data):
    """Crea un usuario via POST /usuarios y devuelve el JSON de respuesta."""
    resp = client.post(
        "/usuarios",
        data=json.dumps(usuario_data),
        content_type="application/json",
    )
    assert resp.status_code == 201, (
        f"No se pudo crear el usuario de apoyo: {resp.get_json()}"
    )
    return resp.get_json()


def _no_password_fields(data: dict) -> bool:
    """Devuelve True si el dict no contiene 'password' ni 'password_hash'."""
    return "password" not in data and "password_hash" not in data


# ---------------------------------------------------------------------------
# POST /usuarios
# ---------------------------------------------------------------------------

class TestCrearUsuario:

    def test_201_creacion_exitosa(self, client, persona_data, usuario_data):
        """Req 5.1 — POST exitoso devuelve 201 con los campos esperados y sin password."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]

        resp = client.post(
            "/usuarios",
            data=json.dumps(usuario_data),
            content_type="application/json",
        )
        assert resp.status_code == 201
        body = resp.get_json()

        # Campos esperados en la respuesta
        assert "id" in body
        assert "persona_id" in body
        assert "username" in body
        assert "created_at" in body
        assert "updated_at" in body

        # Nunca exponer password ni password_hash
        assert _no_password_fields(body), (
            "La respuesta no debe contener 'password' ni 'password_hash'."
        )

        assert body["persona_id"] == persona["id"]
        assert body["username"] == usuario_data["username"]

    def test_400_campo_persona_id_faltante(self, client, persona_data):
        """Req 5.5 — Falta persona_id → 400."""
        crear_persona(client, persona_data)
        payload = {"username": "juanperez", "password": "Secreto123"}

        resp = client.post(
            "/usuarios",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body

    def test_400_campo_username_faltante(self, client, persona_data):
        """Req 5.5 — Falta username → 400."""
        persona = crear_persona(client, persona_data)
        payload = {"persona_id": persona["id"], "password": "Secreto123"}

        resp = client.post(
            "/usuarios",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_400_campo_password_faltante(self, client, persona_data):
        """Req 5.5 — Falta password → 400."""
        persona = crear_persona(client, persona_data)
        payload = {"persona_id": persona["id"], "username": "juanperez"}

        resp = client.post(
            "/usuarios",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_400_password_muy_corto(self, client, persona_data):
        """Req 5.6 — password < 8 caracteres → 400."""
        persona = crear_persona(client, persona_data)
        payload = {
            "persona_id": persona["id"],
            "username": "juanperez",
            "password": "corto",   # 5 chars
        }

        resp = client.post(
            "/usuarios",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert "details" in body
        assert any("password" in d.lower() for d in body["details"])

    def test_400_username_muy_corto(self, client, persona_data):
        """Req 5.7 — username < 3 caracteres → 400."""
        persona = crear_persona(client, persona_data)
        payload = {
            "persona_id": persona["id"],
            "username": "ab",   # 2 chars
            "password": "Secreto123",
        }

        resp = client.post(
            "/usuarios",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert any("username" in d.lower() for d in body["details"])

    def test_400_username_muy_largo(self, client, persona_data):
        """Req 5.7 — username > 50 caracteres → 400."""
        persona = crear_persona(client, persona_data)
        payload = {
            "persona_id": persona["id"],
            "username": "a" * 51,
            "password": "Secreto123",
        }

        resp = client.post(
            "/usuarios",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_404_persona_id_inexistente(self, client):
        """Req 5.3 — persona_id que no existe → 404."""
        payload = {
            "persona_id": 9999,
            "username": "fantasma",
            "password": "Secreto123",
        }

        resp = client.post(
            "/usuarios",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body

    def test_409_username_duplicado(self, client, persona_data, usuario_data):
        """Req 5.2 — username ya existente → 409."""
        # Primera persona y usuario
        persona1 = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona1["id"]
        crear_usuario(client, usuario_data)

        # Segunda persona distinta
        persona_data2 = dict(persona_data)
        persona_data2["documento"] = "99999999"
        persona_data2["email"] = "otro@example.com"
        persona2 = crear_persona(client, persona_data2)

        # Mismo username, persona distinta
        payload = {
            "persona_id": persona2["id"],
            "username": usuario_data["username"],   # duplicado
            "password": "OtraPass456",
        }

        resp = client.post(
            "/usuarios",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 409
        body = resp.get_json()
        assert "error" in body

    def test_409_persona_ya_tiene_usuario(self, client, persona_data, usuario_data):
        """Req 5.4 — misma persona_id usada dos veces (relación 1:1) → 409."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        crear_usuario(client, usuario_data)

        # Segundo usuario con la misma persona
        payload = {
            "persona_id": persona["id"],
            "username": "otrouser",
            "password": "OtraPass456",
        }

        resp = client.post(
            "/usuarios",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# GET /usuarios
# ---------------------------------------------------------------------------

class TestListarUsuarios:

    def test_200_lista_vacia(self, client):
        """Req 6.2 — sin usuarios devuelve lista vacía con 200."""
        resp = client.get("/usuarios")
        assert resp.status_code == 200
        body = resp.get_json()
        assert isinstance(body, list)
        assert body == []

    def test_200_lista_con_usuarios(self, client, persona_data, usuario_data):
        """Req 6.1 — devuelve lista con al menos un elemento y sin password."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        crear_usuario(client, usuario_data)

        resp = client.get("/usuarios")
        assert resp.status_code == 200
        body = resp.get_json()
        assert isinstance(body, list)
        assert len(body) >= 1

        # Ningún elemento debe exponer password ni password_hash
        for item in body:
            assert _no_password_fields(item), (
                f"El item {item} contiene 'password' o 'password_hash'."
            )

    def test_200_campos_esperados(self, client, persona_data, usuario_data):
        """Los items de la lista deben tener id, persona_id, username, created_at, updated_at."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        crear_usuario(client, usuario_data)

        resp = client.get("/usuarios")
        body = resp.get_json()
        item = body[0]

        assert "id" in item
        assert "persona_id" in item
        assert "username" in item
        assert "created_at" in item
        assert "updated_at" in item


# ---------------------------------------------------------------------------
# GET /usuarios/<id>
# ---------------------------------------------------------------------------

class TestObtenerUsuario:

    def test_200_obtener_existente(self, client, persona_data, usuario_data):
        """Req 6.3 — GET por id existente devuelve 200 sin password."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        creado = crear_usuario(client, usuario_data)

        resp = client.get(f"/usuarios/{creado['id']}")
        assert resp.status_code == 200
        body = resp.get_json()

        assert body["id"] == creado["id"]
        assert body["username"] == usuario_data["username"]
        assert body["persona_id"] == persona["id"]
        assert _no_password_fields(body)

    def test_404_id_inexistente(self, client):
        """Req 6.4 — id que no existe → 404."""
        resp = client.get("/usuarios/9999")
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body

    def test_422_id_invalido(self, client):
        """Req 6.5 — id no entero → 422."""
        resp = client.get("/usuarios/abc")
        assert resp.status_code == 422
        body = resp.get_json()
        assert "error" in body

    def test_422_id_negativo(self, client):
        """Req 6.5 — id negativo (no es entero positivo válido) → 422."""
        resp = client.get("/usuarios/-1")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# PUT /usuarios/<id>
# ---------------------------------------------------------------------------

class TestActualizarUsuario:

    def test_200_actualizar_username(self, client, persona_data, usuario_data):
        """Req 7.1 — Actualizar username devuelve 200 sin password."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        creado = crear_usuario(client, usuario_data)

        resp = client.put(
            f"/usuarios/{creado['id']}",
            data=json.dumps({"username": "nuevousername"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        body = resp.get_json()

        assert body["username"] == "nuevousername"
        assert _no_password_fields(body)

    def test_200_actualizar_password_hash_cambia(self, client, persona_data, usuario_data):
        """Req 7.5 — Actualizar password → el hash almacenado cambia; respuesta sin password."""
        from app import create_app, db as _db
        from usuarios.models import Usuario

        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        creado = crear_usuario(client, usuario_data)

        nueva_pass = "NuevaPass789"
        resp = client.put(
            f"/usuarios/{creado['id']}",
            data=json.dumps({"password": nueva_pass}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        body = resp.get_json()

        # Respuesta no debe exponer password
        assert _no_password_fields(body)

        # Verificar que el nuevo hash acepta la nueva contraseña
        # (accedemos al modelo directamente dentro del contexto de la app)
        # El client fixture usa la app con BD en memoria; importamos el db correcto.
        with client.application.app_context():
            usuario = _db.session.get(Usuario, creado["id"])
            assert usuario is not None
            assert usuario.check_password(nueva_pass), (
                "La nueva contraseña no verifica con el hash almacenado."
            )
            assert not usuario.check_password(usuario_data["password"]), (
                "La contraseña vieja no debería verificar tras la actualización."
            )

    def test_400_cuerpo_vacio(self, client, persona_data, usuario_data):
        """Req 7.6 — Cuerpo vacío o sin campos modificables → 400."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        creado = crear_usuario(client, usuario_data)

        resp = client.put(
            f"/usuarios/{creado['id']}",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body

    def test_400_password_muy_corto(self, client, persona_data, usuario_data):
        """Req 7.4 — password < 8 en PUT → 400."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        creado = crear_usuario(client, usuario_data)

        resp = client.put(
            f"/usuarios/{creado['id']}",
            data=json.dumps({"password": "corto"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_400_password_muy_largo(self, client, persona_data, usuario_data):
        """Req 7.4 — password > 128 en PUT → 400."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        creado = crear_usuario(client, usuario_data)

        resp = client.put(
            f"/usuarios/{creado['id']}",
            data=json.dumps({"password": "x" * 129}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_404_id_inexistente(self, client):
        """Req 7.2 — PUT en id que no existe → 404."""
        resp = client.put(
            "/usuarios/9999",
            data=json.dumps({"username": "nadie"}),
            content_type="application/json",
        )
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body

    def test_409_username_duplicado_en_put(self, client, persona_data, usuario_data):
        """Req 7.3 — username ya pertenece a otro usuario → 409."""
        # Usuario 1
        persona1 = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona1["id"]
        usuario1 = crear_usuario(client, usuario_data)

        # Usuario 2 con persona y username distintos
        persona_data2 = dict(persona_data)
        persona_data2["documento"] = "88888888"
        persona_data2["email"] = "otro2@example.com"
        persona2 = crear_persona(client, persona_data2)
        payload2 = {
            "persona_id": persona2["id"],
            "username": "segundousuario",
            "password": "OtraPass456",
        }
        usuario2 = crear_usuario(client, payload2)

        # Intentar cambiar el username del usuario2 al del usuario1
        resp = client.put(
            f"/usuarios/{usuario2['id']}",
            data=json.dumps({"username": usuario1["username"]}),
            content_type="application/json",
        )
        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# DELETE /usuarios/<id>
# ---------------------------------------------------------------------------

class TestEliminarUsuario:

    def test_204_eliminacion_exitosa(self, client, persona_data, usuario_data):
        """Req 8.1 — DELETE exitoso devuelve 204 sin cuerpo."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        creado = crear_usuario(client, usuario_data)

        resp = client.delete(f"/usuarios/{creado['id']}")
        assert resp.status_code == 204
        assert resp.data == b""

    def test_204_usuario_ya_no_existe_tras_delete(self, client, persona_data, usuario_data):
        """Verificar que tras el DELETE el GET devuelve 404."""
        persona = crear_persona(client, persona_data)
        usuario_data["persona_id"] = persona["id"]
        creado = crear_usuario(client, usuario_data)

        client.delete(f"/usuarios/{creado['id']}")

        resp = client.get(f"/usuarios/{creado['id']}")
        assert resp.status_code == 404

    def test_400_id_no_entero(self, client):
        """Req 8.3 — id no entero en DELETE → 400 (no 422)."""
        resp = client.delete("/usuarios/abc")
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body

    def test_400_id_negativo(self, client):
        """Req 8.3 — id negativo en DELETE → 400."""
        resp = client.delete("/usuarios/-5")
        assert resp.status_code == 400

    def test_404_id_inexistente(self, client):
        """Req 8.2 — id que no existe → 404."""
        resp = client.delete("/usuarios/9999")
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body
