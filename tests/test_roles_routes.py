import pytest


def crear_persona(client, data):
    resp = client.post("/personas", json=data)
    assert resp.status_code == 201
    return resp.get_json()


def crear_usuario(client, data):
    resp = client.post("/usuarios", json=data)
    assert resp.status_code == 201
    return resp.get_json()


def crear_rol(client, nombre="Admin", descripcion=None):
    data = {"nombre": nombre}
    if descripcion:
        data["descripcion"] = descripcion
    resp = client.post("/roles", json=data)
    assert resp.status_code == 201
    return resp.get_json()


class TestCrearRol:

    def test_201_creacion_exitosa(self, client):
        resp = client.post("/roles", json={"nombre": "Admin"})
        assert resp.status_code == 201
        body = resp.get_json()
        for campo in ("id", "nombre", "descripcion", "created_at", "updated_at", "permisos"):
            assert campo in body
        assert body["nombre"] == "Admin"

    def test_400_nombre_faltante(self, client):
        resp = client.post("/roles", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_nombre_vacio(self, client):
        resp = client.post("/roles", json={"nombre": ""})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_nombre_demasiado_largo(self, client):
        resp = client.post("/roles", json={"nombre": "A" * 51})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_409_nombre_duplicado(self, client):
        crear_rol(client, nombre="Admin")
        resp = client.post("/roles", json={"nombre": "Admin"})
        assert resp.status_code == 409
        assert "error" in resp.get_json()


class TestListarRoles:

    def test_200_lista_vacia(self, client):
        resp = client.get("/roles")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_200_lista_con_rol(self, client):
        crear_rol(client, nombre="Admin")
        resp = client.get("/roles")
        assert resp.status_code == 200
        body = resp.get_json()
        assert isinstance(body, list)
        assert len(body) >= 1

    def test_200_items_contienen_campos_esperados(self, client):
        crear_rol(client, nombre="Editor")
        resp = client.get("/roles")
        body = resp.get_json()
        item = body[0]
        for campo in ("id", "nombre", "descripcion", "permisos"):
            assert campo in item


class TestObtenerRol:

    def test_200_rol_existente(self, client):
        rol = crear_rol(client, nombre="Admin")
        resp = client.get(f"/roles/{rol['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == rol["id"]

    def test_404_id_inexistente(self, client):
        resp = client.get("/roles/9999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_422_id_no_entero(self, client):
        resp = client.get("/roles/abc")
        assert resp.status_code == 422
        assert "error" in resp.get_json()

    def test_422_id_cero(self, client):
        resp = client.get("/roles/0")
        assert resp.status_code == 422

    def test_422_id_negativo(self, client):
        resp = client.get("/roles/-1")
        assert resp.status_code == 422


class TestActualizarRol:

    def test_200_actualiza_nombre(self, client):
        rol = crear_rol(client, nombre="Admin")
        resp = client.put(f"/roles/{rol['id']}", json={"nombre": "SuperAdmin"})
        assert resp.status_code == 200
        assert resp.get_json()["nombre"] == "SuperAdmin"

    def test_200_actualiza_descripcion(self, client):
        rol = crear_rol(client, nombre="Editor")
        resp = client.put(f"/roles/{rol['id']}", json={"descripcion": "Rol de edición"})
        assert resp.status_code == 200
        assert resp.get_json()["descripcion"] == "Rol de edición"

    def test_400_cuerpo_vacio(self, client):
        rol = crear_rol(client, nombre="Admin")
        resp = client.put(f"/roles/{rol['id']}", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_campos_no_reconocidos(self, client):
        rol = crear_rol(client, nombre="Admin")
        resp = client.put(f"/roles/{rol['id']}", json={"campo_raro": "valor"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_nombre_vacio(self, client):
        rol = crear_rol(client, nombre="Admin")
        resp = client.put(f"/roles/{rol['id']}", json={"nombre": ""})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_404_id_inexistente(self, client):
        resp = client.put("/roles/9999", json={"nombre": "Nuevo"})
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_409_nombre_duplicado_en_otro_rol(self, client):
        crear_rol(client, nombre="Admin")
        rol2 = crear_rol(client, nombre="Editor")
        resp = client.put(f"/roles/{rol2['id']}", json={"nombre": "Admin"})
        assert resp.status_code == 409
        assert "error" in resp.get_json()


class TestEliminarRol:

    def test_204_eliminacion_exitosa(self, client):
        rol = crear_rol(client, nombre="Temporal")
        resp = client.delete(f"/roles/{rol['id']}")
        assert resp.status_code == 204
        assert resp.data == b""

    def test_204_get_devuelve_404_tras_delete(self, client):
        rol = crear_rol(client, nombre="Borrable")
        client.delete(f"/roles/{rol['id']}")
        resp = client.get(f"/roles/{rol['id']}")
        assert resp.status_code == 404

    def test_404_id_inexistente(self, client):
        resp = client.delete("/roles/9999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_409_rol_con_usuarios_asignados(self, client, persona_data):
        persona = crear_persona(client, persona_data)
        usuario = crear_usuario(client, {
            "persona_id": persona["id"],
            "username": "testuser",
            "password": "Secreto123",
        })
        rol = crear_rol(client, nombre="ConUsuarios")
        client.post(f"/usuarios/{usuario['id']}/roles", json={"rol_id": rol["id"]})
        resp = client.delete(f"/roles/{rol['id']}")
        assert resp.status_code == 409
        assert "error" in resp.get_json()

    def test_422_id_no_entero(self, client):
        resp = client.delete("/roles/abc")
        assert resp.status_code == 422


class TestListarRolesDeUsuario:

    def test_200_lista_vacia_antes_de_asignar(self, client, persona_data):
        persona = crear_persona(client, persona_data)
        usuario = crear_usuario(client, {
            "persona_id": persona["id"],
            "username": "sinroles",
            "password": "Secreto123",
        })
        resp = client.get(f"/usuarios/{usuario['id']}/roles")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_200_lista_con_rol_asignado(self, client, persona_data):
        persona = crear_persona(client, persona_data)
        usuario = crear_usuario(client, {
            "persona_id": persona["id"],
            "username": "conrol",
            "password": "Secreto123",
        })
        rol = crear_rol(client, nombre="Viewer")
        client.post(f"/usuarios/{usuario['id']}/roles", json={"rol_id": rol["id"]})
        resp = client.get(f"/usuarios/{usuario['id']}/roles")
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body) == 1
        assert body[0]["id"] == rol["id"]

    def test_404_usuario_inexistente(self, client):
        resp = client.get("/usuarios/9999/roles")
        assert resp.status_code == 404
        assert "error" in resp.get_json()


class TestAsignarRolAUsuario:

    def test_200_asignacion_exitosa(self, client, persona_data):
        persona = crear_persona(client, persona_data)
        usuario = crear_usuario(client, {
            "persona_id": persona["id"],
            "username": "asignado",
            "password": "Secreto123",
        })
        rol = crear_rol(client, nombre="Moderador")
        resp = client.post(f"/usuarios/{usuario['id']}/roles", json={"rol_id": rol["id"]})
        assert resp.status_code == 200
        body = resp.get_json()
        assert isinstance(body, list)
        assert any(r["id"] == rol["id"] for r in body)

    def test_400_rol_id_faltante(self, client, persona_data):
        persona = crear_persona(client, persona_data)
        usuario = crear_usuario(client, {
            "persona_id": persona["id"],
            "username": "sinrolid",
            "password": "Secreto123",
        })
        resp = client.post(f"/usuarios/{usuario['id']}/roles", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_404_usuario_inexistente(self, client):
        rol = crear_rol(client, nombre="Fantasma")
        resp = client.post("/usuarios/9999/roles", json={"rol_id": rol["id"]})
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_404_rol_inexistente(self, client, persona_data):
        persona = crear_persona(client, persona_data)
        usuario = crear_usuario(client, {
            "persona_id": persona["id"],
            "username": "rolinexistente",
            "password": "Secreto123",
        })
        resp = client.post(f"/usuarios/{usuario['id']}/roles", json={"rol_id": 9999})
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_409_asignacion_duplicada(self, client, persona_data):
        persona = crear_persona(client, persona_data)
        usuario = crear_usuario(client, {
            "persona_id": persona["id"],
            "username": "duplicado",
            "password": "Secreto123",
        })
        rol = crear_rol(client, nombre="Duplicable")
        client.post(f"/usuarios/{usuario['id']}/roles", json={"rol_id": rol["id"]})
        resp = client.post(f"/usuarios/{usuario['id']}/roles", json={"rol_id": rol["id"]})
        assert resp.status_code == 409
        assert "error" in resp.get_json()


class TestDesasignarRolDeUsuario:

    def test_204_desasignacion_exitosa(self, client, persona_data):
        persona = crear_persona(client, persona_data)
        usuario = crear_usuario(client, {
            "persona_id": persona["id"],
            "username": "quitarrol",
            "password": "Secreto123",
        })
        rol = crear_rol(client, nombre="Removible")
        client.post(f"/usuarios/{usuario['id']}/roles", json={"rol_id": rol["id"]})
        resp = client.delete(f"/usuarios/{usuario['id']}/roles/{rol['id']}")
        assert resp.status_code == 204
        assert resp.data == b""

    def test_404_usuario_inexistente(self, client):
        rol = crear_rol(client, nombre="Huerfano")
        resp = client.delete(f"/usuarios/9999/roles/{rol['id']}")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_404_rol_no_asignado(self, client, persona_data):
        persona = crear_persona(client, persona_data)
        usuario = crear_usuario(client, {
            "persona_id": persona["id"],
            "username": "sineste",
            "password": "Secreto123",
        })
        rol = crear_rol(client, nombre="NoAsignado")
        resp = client.delete(f"/usuarios/{usuario['id']}/roles/{rol['id']}")
        assert resp.status_code == 404
        assert "error" in resp.get_json()
