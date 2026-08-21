import pytest


def crear_sistema(client, nombre="ERP", descripcion=None):
    data = {"nombre": nombre}
    if descripcion:
        data["descripcion"] = descripcion
    resp = client.post("/sistemas", json=data)
    assert resp.status_code == 201
    return resp.get_json()


def crear_permiso(client, sistema_id, nombre="leer"):
    resp = client.post("/permisos", json={"sistema_id": sistema_id, "nombre": nombre})
    assert resp.status_code == 201
    return resp.get_json()


class TestCrearSistema:

    def test_201_con_datos_validos(self, client):
        resp = client.post("/sistemas", json={"nombre": "ERP"})
        assert resp.status_code == 201

    def test_respuesta_contiene_todos_los_campos(self, client):
        resp = client.post("/sistemas", json={"nombre": "ERP"})
        body = resp.get_json()
        for campo in ("id", "nombre", "descripcion", "created_at", "updated_at"):
            assert campo in body, f"Campo '{campo}' ausente en la respuesta"

    def test_400_nombre_faltante(self, client):
        resp = client.post("/sistemas", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_nombre_cadena_vacia(self, client):
        resp = client.post("/sistemas", json={"nombre": ""})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_nombre_101_caracteres(self, client):
        resp = client.post("/sistemas", json={"nombre": "A" * 101})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_409_nombre_duplicado(self, client):
        crear_sistema(client, nombre="ERP")
        resp = client.post("/sistemas", json={"nombre": "ERP"})
        assert resp.status_code == 409
        assert "error" in resp.get_json()


class TestListarSistemas:

    def test_200_lista_vacia_inicialmente(self, client):
        resp = client.get("/sistemas")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_200_lista_despues_de_creacion(self, client):
        crear_sistema(client, nombre="ERP")
        resp = client.get("/sistemas")
        assert resp.status_code == 200
        body = resp.get_json()
        assert isinstance(body, list)
        assert len(body) >= 1

    def test_200_cada_item_tiene_campos_esperados(self, client):
        crear_sistema(client, nombre="ERP")
        resp = client.get("/sistemas")
        assert resp.status_code == 200
        for item in resp.get_json():
            for campo in ("id", "nombre", "descripcion"):
                assert campo in item, f"Campo '{campo}' ausente en item del listado"


class TestObtenerSistema:

    def test_200_sistema_existente(self, client):
        creado = crear_sistema(client, nombre="ERP")
        resp = client.get(f"/sistemas/{creado['id']}")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["id"] == creado["id"]
        assert body["nombre"] == "ERP"

    def test_404_id_inexistente(self, client):
        resp = client.get("/sistemas/9999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_422_id_no_entero(self, client):
        resp = client.get("/sistemas/abc")
        assert resp.status_code == 422
        assert "error" in resp.get_json()

    def test_422_id_cero(self, client):
        resp = client.get("/sistemas/0")
        assert resp.status_code == 422

    def test_422_id_negativo(self, client):
        resp = client.get("/sistemas/-1")
        assert resp.status_code == 422


class TestActualizarSistema:

    def test_200_actualiza_nombre(self, client):
        creado = crear_sistema(client, nombre="ERP")
        resp = client.put(f"/sistemas/{creado['id']}", json={"nombre": "CRM"})
        assert resp.status_code == 200
        assert resp.get_json()["nombre"] == "CRM"

    def test_200_actualiza_solo_descripcion(self, client):
        creado = crear_sistema(client, nombre="ERP")
        resp = client.put(f"/sistemas/{creado['id']}", json={"descripcion": "Sistema ERP principal"})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["descripcion"] == "Sistema ERP principal"
        assert body["nombre"] == "ERP"

    def test_400_cuerpo_vacio(self, client):
        creado = crear_sistema(client, nombre="ERP")
        resp = client.put(f"/sistemas/{creado['id']}", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_campos_no_reconocidos(self, client):
        creado = crear_sistema(client, nombre="ERP")
        resp = client.put(f"/sistemas/{creado['id']}", json={"campo_inexistente": "valor"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_400_nombre_cadena_vacia(self, client):
        creado = crear_sistema(client, nombre="ERP")
        resp = client.put(f"/sistemas/{creado['id']}", json={"nombre": ""})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_404_id_inexistente(self, client):
        resp = client.put("/sistemas/9999", json={"nombre": "Nuevo"})
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_409_nombre_ya_usado_por_otro_sistema(self, client):
        crear_sistema(client, nombre="ERP")
        segundo = crear_sistema(client, nombre="CRM")
        resp = client.put(f"/sistemas/{segundo['id']}", json={"nombre": "ERP"})
        assert resp.status_code == 409
        assert "error" in resp.get_json()


class TestEliminarSistema:

    def test_204_sin_cuerpo_en_respuesta(self, client):
        creado = crear_sistema(client, nombre="ERP")
        resp = client.delete(f"/sistemas/{creado['id']}")
        assert resp.status_code == 204
        assert resp.data == b""

    def test_204_y_get_devuelve_404(self, client):
        creado = crear_sistema(client, nombre="ERP")
        client.delete(f"/sistemas/{creado['id']}")
        resp = client.get(f"/sistemas/{creado['id']}")
        assert resp.status_code == 404

    def test_404_id_inexistente(self, client):
        resp = client.delete("/sistemas/9999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_409_sistema_con_permisos_asociados(self, client):
        sistema = crear_sistema(client, nombre="ERP")
        crear_permiso(client, sistema["id"], nombre="leer")
        resp = client.delete(f"/sistemas/{sistema['id']}")
        assert resp.status_code == 409
        assert "error" in resp.get_json()

    def test_422_id_no_entero(self, client):
        resp = client.delete("/sistemas/abc")
        assert resp.status_code == 422
