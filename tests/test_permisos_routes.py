import pytest


def crear_sistema(client, nombre="ERP"):
    resp = client.post("/sistemas", json={"nombre": nombre})
    assert resp.status_code == 201
    return resp.get_json()


def crear_permiso(client, sistema_id, nombre="leer"):
    resp = client.post("/permisos", json={"sistema_id": sistema_id, "nombre": nombre})
    assert resp.status_code == 201
    return resp.get_json()


def crear_rol(client, nombre="Admin"):
    resp = client.post("/roles", json={"nombre": nombre})
    assert resp.status_code == 201
    return resp.get_json()


class TestCrearPermiso:

    def test_201_con_datos_validos(self, client):
        sistema = crear_sistema(client)
        resp = client.post("/permisos", json={"sistema_id": sistema["id"], "nombre": "leer"})
        assert resp.status_code == 201

    def test_respuesta_contiene_todos_los_campos(self, client):
        sistema = crear_sistema(client)
        resp = client.post("/permisos", json={"sistema_id": sistema["id"], "nombre": "leer"})
        body = resp.get_json()
        for campo in ("id", "sistema_id", "nombre", "descripcion", "sistema", "created_at", "updated_at"):
            assert campo in body

    def test_400_nombre_faltante(self, client):
        sistema = crear_sistema(client)
        resp = client.post("/permisos", json={"sistema_id": sistema["id"]})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_sistema_id_faltante(self, client):
        resp = client.post("/permisos", json={"nombre": "leer"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_nombre_vacio(self, client):
        sistema = crear_sistema(client)
        resp = client.post("/permisos", json={"sistema_id": sistema["id"], "nombre": ""})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_nombre_101_caracteres(self, client):
        sistema = crear_sistema(client)
        resp = client.post("/permisos", json={"sistema_id": sistema["id"], "nombre": "a" * 101})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_404_sistema_id_inexistente(self, client):
        resp = client.post("/permisos", json={"sistema_id": 9999, "nombre": "leer"})
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_409_par_sistema_nombre_duplicado(self, client):
        sistema = crear_sistema(client)
        crear_permiso(client, sistema["id"], "leer")
        resp = client.post("/permisos", json={"sistema_id": sistema["id"], "nombre": "leer"})
        assert resp.status_code == 409
        assert "error" in resp.get_json()


class TestListarPermisos:

    def test_200_lista_vacia_inicialmente(self, client):
        resp = client.get("/permisos")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_200_lista_con_permisos_tras_creacion(self, client):
        sistema = crear_sistema(client)
        crear_permiso(client, sistema["id"])
        resp = client.get("/permisos")
        assert resp.status_code == 200
        body = resp.get_json()
        assert isinstance(body, list)
        assert len(body) >= 1

    def test_200_items_tienen_campos_esperados(self, client):
        sistema = crear_sistema(client)
        crear_permiso(client, sistema["id"])
        resp = client.get("/permisos")
        body = resp.get_json()
        for item in body:
            assert "id" in item
            assert "sistema_id" in item
            assert "nombre" in item


class TestObtenerPermiso:

    def test_200_retorna_permiso_correcto_con_sistema(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        resp = client.get(f"/permisos/{permiso['id']}")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["id"] == permiso["id"]
        assert "sistema" in body
        assert body["sistema"] is not None

    def test_404_id_inexistente(self, client):
        resp = client.get("/permisos/9999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_422_id_no_entero(self, client):
        resp = client.get("/permisos/abc")
        assert resp.status_code == 422
        assert "error" in resp.get_json()

    def test_422_id_cero(self, client):
        resp = client.get("/permisos/0")
        assert resp.status_code == 422


class TestActualizarPermiso:

    def test_200_actualiza_nombre(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        resp = client.put(f"/permisos/{permiso['id']}", json={"nombre": "escribir"})
        assert resp.status_code == 200
        assert resp.get_json()["nombre"] == "escribir"

    def test_200_actualiza_solo_descripcion(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        resp = client.put(f"/permisos/{permiso['id']}", json={"descripcion": "Permite leer"})
        assert resp.status_code == 200
        assert resp.get_json()["descripcion"] == "Permite leer"

    def test_400_cuerpo_vacio(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        resp = client.put(f"/permisos/{permiso['id']}", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_nombre_vacio(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        resp = client.put(f"/permisos/{permiso['id']}", json={"nombre": ""})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_404_id_inexistente(self, client):
        resp = client.put("/permisos/9999", json={"nombre": "nuevo"})
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_409_nombre_duplicado_en_mismo_sistema(self, client):
        sistema = crear_sistema(client)
        crear_permiso(client, sistema["id"], "leer")
        permiso2 = crear_permiso(client, sistema["id"], "escribir")
        resp = client.put(f"/permisos/{permiso2['id']}", json={"nombre": "leer"})
        assert resp.status_code == 409
        assert "error" in resp.get_json()


class TestEliminarPermiso:

    def test_204_sin_cuerpo(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        resp = client.delete(f"/permisos/{permiso['id']}")
        assert resp.status_code == 204
        assert resp.data == b""

    def test_204_luego_get_retorna_404(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        client.delete(f"/permisos/{permiso['id']}")
        resp = client.get(f"/permisos/{permiso['id']}")
        assert resp.status_code == 404

    def test_404_id_inexistente(self, client):
        resp = client.delete("/permisos/9999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_422_id_no_entero(self, client):
        resp = client.delete("/permisos/abc")
        assert resp.status_code == 422
        assert "error" in resp.get_json()


class TestListarPermisosDeRol:

    def test_200_lista_vacia_antes_de_asignar(self, client):
        rol = crear_rol(client)
        resp = client.get(f"/roles/{rol['id']}/permisos")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_200_lista_con_permiso_tras_asignacion(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        rol = crear_rol(client)
        client.post(f"/roles/{rol['id']}/permisos", json={"permiso_id": permiso["id"]})
        resp = client.get(f"/roles/{rol['id']}/permisos")
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body) == 1
        assert body[0]["id"] == permiso["id"]

    def test_404_rol_inexistente(self, client):
        resp = client.get("/roles/9999/permisos")
        assert resp.status_code == 404
        assert "error" in resp.get_json()


class TestAsignarPermisoARol:

    def test_200_retorna_lista_actualizada(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        rol = crear_rol(client)
        resp = client.post(f"/roles/{rol['id']}/permisos", json={"permiso_id": permiso["id"]})
        assert resp.status_code == 200
        body = resp.get_json()
        assert isinstance(body, list)
        assert any(p["id"] == permiso["id"] for p in body)

    def test_400_permiso_id_faltante(self, client):
        rol = crear_rol(client)
        resp = client.post(f"/roles/{rol['id']}/permisos", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_404_rol_inexistente(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        resp = client.post("/roles/9999/permisos", json={"permiso_id": permiso["id"]})
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_404_permiso_id_inexistente(self, client):
        rol = crear_rol(client)
        resp = client.post(f"/roles/{rol['id']}/permisos", json={"permiso_id": 9999})
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_409_asignar_mismo_permiso_dos_veces(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        rol = crear_rol(client)
        client.post(f"/roles/{rol['id']}/permisos", json={"permiso_id": permiso["id"]})
        resp = client.post(f"/roles/{rol['id']}/permisos", json={"permiso_id": permiso["id"]})
        assert resp.status_code == 409
        assert "error" in resp.get_json()


class TestDesasignarPermisoDeRol:

    def test_204_desasignacion_exitosa(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        rol = crear_rol(client)
        client.post(f"/roles/{rol['id']}/permisos", json={"permiso_id": permiso["id"]})
        resp = client.delete(f"/roles/{rol['id']}/permisos/{permiso['id']}")
        assert resp.status_code == 204

    def test_404_rol_inexistente(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        resp = client.delete(f"/roles/9999/permisos/{permiso['id']}")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_404_permiso_no_asignado_al_rol(self, client):
        sistema = crear_sistema(client)
        permiso = crear_permiso(client, sistema["id"])
        rol = crear_rol(client)
        resp = client.delete(f"/roles/{rol['id']}/permisos/{permiso['id']}")
        assert resp.status_code == 404
        assert "error" in resp.get_json()
