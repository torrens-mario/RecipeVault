import pytest


def test_toggle_favorito(client, auth_headers, recipe):
    assert recipe["favorite"] is False

    r = client.post(f"/api/recipes/{recipe['id']}/favorite", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["favorite"] is True

    r2 = client.post(f"/api/recipes/{recipe['id']}/favorite", headers=auth_headers)
    assert r2.status_code == 200
    assert r2.json()["favorite"] is False


def test_receta_publica_accesible_sin_login(client, auth_headers, recipe):
    r = client.get(f"/api/shared/{recipe['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == recipe["id"]


def test_receta_privada_no_accesible_sin_login(client, auth_headers, recipe):
    client.post(f"/api/recipes/{recipe['id']}/public", headers=auth_headers)

    r = client.get(f"/api/shared/{recipe['id']}")
    assert r.status_code == 404


def test_toggle_plan(client, auth_headers, recipe):
    assert recipe["planned_to_cook"] is False

    r = client.post(f"/api/recipes/{recipe['id']}/plan", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["planned_to_cook"] is True

    r2 = client.post(f"/api/recipes/{recipe['id']}/plan", headers=auth_headers)
    assert r2.status_code == 200
    assert r2.json()["planned_to_cook"] is False


def test_auth_me(client, auth_headers, new_user):
    r = client.get("/api/auth/me", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == new_user["username"]
    assert data["email"] == new_user["email"]


def test_inventario_low_stock(client, auth_headers):
    client.post("/api/inventory", headers=auth_headers, json={
        "name": "Pimentón escaso",
        "quantity": 3,
        "unit": "g",
        "low_stock_threshold": 10,
        "low_stock_unit": "g",
    })

    r = client.get("/api/inventory/low-stock", headers=auth_headers)
    assert r.status_code == 200
    items = r.json()
    assert any(x["name"] == "Pimentón escaso" for x in items)
