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
