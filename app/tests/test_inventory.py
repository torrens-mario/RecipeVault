import pytest


def test_crear_item_inventario(client, auth_headers):
    r = client.post("/api/inventory", headers=auth_headers, json={
        "name": "Arroz",
        "quantity": 1000,
        "unit": "g",
        "low_stock_threshold": 200,
        "low_stock_unit": "g",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Arroz"
    assert data["quantity"] == 1000
    assert data["unit"] == "g"
    assert "id" in data


def test_listar_inventario_incluye_item_creado(client, auth_headers, inventory_item):
    r = client.get("/api/inventory", headers=auth_headers)
    assert r.status_code == 200
    ids = [x["id"] for x in r.json()]
    assert inventory_item["id"] in ids


def test_actualizar_cantidad_item(client, auth_headers, inventory_item):
    r = client.put(f"/api/inventory/{inventory_item['id']}", headers=auth_headers, json={
        "name": inventory_item["name"],
        "quantity": 250,
        "unit": inventory_item["unit"],
        "low_stock_threshold": inventory_item["low_stock_threshold"],
        "low_stock_unit": inventory_item["low_stock_unit"],
    })
    assert r.status_code == 200
    assert r.json()["quantity"] == 250


def test_eliminar_item_inventario(client, auth_headers, inventory_item):
    r = client.delete(f"/api/inventory/{inventory_item['id']}", headers=auth_headers)
    assert r.status_code == 204
    items = client.get("/api/inventory", headers=auth_headers).json()
    assert not any(x["id"] == inventory_item["id"] for x in items)


def test_actualizar_item_inexistente_devuelve_404(client, auth_headers):
    r = client.put("/api/inventory/999999", headers=auth_headers, json={
        "name": "No existe",
        "quantity": 100,
        "unit": "g",
        "low_stock_threshold": 10,
        "low_stock_unit": "g",
    })
    assert r.status_code == 404


def test_eliminar_item_inexistente_devuelve_404(client, auth_headers):
    r = client.delete("/api/inventory/999999", headers=auth_headers)
    assert r.status_code == 404


def test_shopping_list_devuelve_estructura_correcta(client, auth_headers):
    r = client.get("/api/shopping-list", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "low_stock" in data
    assert "planned_recipes" in data
    assert "missing_for_planned" in data
