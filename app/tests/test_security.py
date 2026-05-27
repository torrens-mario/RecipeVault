"""
Tests de aislamiento entre usuarios:
- Usuario B no puede leer, modificar ni eliminar recetas del usuario A
- Usuario B no puede ver el inventario del usuario A
"""
import uuid


def _register(client):
    suffix = uuid.uuid4().hex[:8]
    r = client.post("/api/auth/register", json={
        "username": f"sec_{suffix}",
        "email": f"sec_{suffix}@test.com",
        "password": "testpass123",
    })
    assert r.status_code == 201
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _crear_receta(client, headers):
    r = client.post("/api/recipes", headers=headers, json={
        "title": "Receta privada",
        "description": "",
        "category": "Test",
        "servings": 2,
        "ingredients": [],
        "steps": [],
        "tags": [],
    })
    assert r.status_code == 201
    return r.json()


def test_usuario_b_no_puede_leer_receta_de_a(client):
    headers_a = _register(client)
    headers_b = _register(client)
    receta = _crear_receta(client, headers_a)

    r = client.get(f"/api/recipes/{receta['id']}", headers=headers_b)
    assert r.status_code == 404


def test_usuario_b_no_puede_modificar_receta_de_a(client):
    headers_a = _register(client)
    headers_b = _register(client)
    receta = _crear_receta(client, headers_a)

    r = client.put(f"/api/recipes/{receta['id']}", headers=headers_b, json={
        **receta,
        "title": "Intento de hackeo",
    })
    assert r.status_code == 404


def test_usuario_b_no_puede_eliminar_receta_de_a(client):
    headers_a = _register(client)
    headers_b = _register(client)
    receta = _crear_receta(client, headers_a)

    r = client.delete(f"/api/recipes/{receta['id']}", headers=headers_b)
    assert r.status_code == 404


def test_usuario_b_no_puede_modificar_inventario_de_a(client):
    headers_a = _register(client)
    headers_b = _register(client)

    r = client.post("/api/inventory", headers=headers_a, json={
        "name": "Sal exclusiva",
        "quantity": 100,
        "unit": "g",
        "low_stock_threshold": 10,
        "low_stock_unit": "g",
    })
    assert r.status_code == 201
    item_id = r.json()["id"]

    r2 = client.put(f"/api/inventory/{item_id}", headers=headers_b, json={
        "name": "Sal hackeada",
        "quantity": 999,
        "unit": "g",
        "low_stock_threshold": 10,
        "low_stock_unit": "g",
    })
    assert r2.status_code == 404


def test_usuario_b_no_puede_eliminar_inventario_de_a(client):
    headers_a = _register(client)
    headers_b = _register(client)

    r = client.post("/api/inventory", headers=headers_a, json={
        "name": "Pimienta exclusiva",
        "quantity": 50,
        "unit": "g",
        "low_stock_threshold": 5,
        "low_stock_unit": "g",
    })
    assert r.status_code == 201
    item_id = r.json()["id"]

    r2 = client.delete(f"/api/inventory/{item_id}", headers=headers_b)
    assert r2.status_code == 404


def test_usuario_b_no_ve_inventario_de_a(client):
    headers_a = _register(client)
    headers_b = _register(client)

    r = client.post("/api/inventory", headers=headers_a, json={
        "name": "Ingrediente secreto",
        "quantity": 100,
        "unit": "g",
        "low_stock_threshold": 10,
        "low_stock_unit": "g",
    })
    assert r.status_code == 201
    item_id = r.json()["id"]

    inventario_b = client.get("/api/inventory", headers=headers_b).json()
    assert not any(x["id"] == item_id for x in inventario_b)
