class TestFlujoRBAC:

    def test_flujo_completo_rbac(self, client, persona_data, usuario_data):
        resp = client.post("/sistemas", json={"nombre": "Facturacion"})
        assert resp.status_code == 201
        sistema = resp.get_json()

        resp = client.post("/permisos", json={"sistema_id": sistema["id"], "nombre": "emitir_factura"})
        assert resp.status_code == 201
        permiso = resp.get_json()

        resp = client.post("/roles", json={"nombre": "Contador"})
        assert resp.status_code == 201
        rol = resp.get_json()

        resp = client.post(f"/roles/{rol['id']}/permisos", json={"permiso_id": permiso["id"]})
        assert resp.status_code == 200

        resp = client.post("/personas", json=persona_data)
        assert resp.status_code == 201
        persona = resp.get_json()

        usuario_data["persona_id"] = persona["id"]
        resp = client.post("/usuarios", json=usuario_data)
        assert resp.status_code == 201
        usuario = resp.get_json()

        resp = client.post(f"/usuarios/{usuario['id']}/roles", json={"rol_id": rol["id"]})
        assert resp.status_code == 200

        resp = client.get(f"/usuarios/{usuario['id']}/roles")
        assert resp.status_code == 200
        roles = resp.get_json()
        assert any(r["id"] == rol["id"] for r in roles)

        resp = client.get(f"/roles/{rol['id']}/permisos")
        assert resp.status_code == 200
        permisos = resp.get_json()
        assert any(p["id"] == permiso["id"] for p in permisos)
