"""
Tests de validación de entrada:
- Registro duplicado → 400
- Inventario con cantidad inválida → 400
- Receta con título vacío → 422
- Búsqueda de recetas por nombre
"""
import uuid


def test_registro_duplicado_devuelve_400(client, new_user):
    r = client.post("/api/auth/register", json={
        "username": new_user["username"],
        "email": new_user["email"],
        "password": "otrapass123",
    })
    assert r.status_code == 400


def test_registro_email_duplicado_devuelve_400(client, new_user):
    suffix = uuid.uuid4().hex[:8]
    r = client.post("/api/auth/register", json={
        "username": f"distinto_{suffix}",
        "email": new_user["email"],
        "password": "otrapass123",
    })
    assert r.status_code == 400


def test_inventario_cantidad_negativa_devuelve_400(client, auth_headers):
    r = client.post("/api/inventory", headers=auth_headers, json={
        "name": "Test",
        "quantity": -10,
        "unit": "g",
        "low_stock_threshold": 5,
        "low_stock_unit": "g",
    })
    assert r.status_code == 400


def test_inventario_cantidad_texto_devuelve_400(client, auth_headers):
    r = client.post("/api/inventory", headers=auth_headers, json={
        "name": "Test",
        "quantity": "mucho",
        "unit": "g",
        "low_stock_threshold": 5,
        "low_stock_unit": "g",
    })
    assert r.status_code == 400


def test_receta_titulo_vacio_devuelve_422(client, auth_headers):
    r = client.post("/api/recipes", headers=auth_headers, json={
        "title": "",
        "description": "",
        "category": "Test",
        "servings": 2,
        "ingredients": [],
        "steps": [],
        "tags": [],
    })
    assert r.status_code == 422


def test_busqueda_recetas_por_nombre(client, auth_headers):
    suffix = uuid.uuid4().hex[:6]
    titulo = f"GazpachoUnico_{suffix}"
    client.post("/api/recipes", headers=auth_headers, json={
        "title": titulo,
        "description": "Sopa fría de tomate",
        "category": "Sopas",
        "servings": 4,
        "ingredients": [],
        "steps": [],
        "tags": [],
    })

    r = client.get(f"/api/recipes?q={titulo}", headers=auth_headers)
    assert r.status_code == 200
    assert any(x["title"] == titulo for x in r.json())


def test_busqueda_sin_resultados(client, auth_headers):
    r = client.get("/api/recipes?q=xyzzy_inexistente_42", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []
