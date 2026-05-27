import pytest


def test_crear_receta_asigna_imagen_automatica(client, auth_headers):
    r = client.post("/api/recipes", headers=auth_headers, json={
        "title": "Pasta carbonara",
        "description": "Con panceta y huevo, sin nata",
        "category": "Italiana",
        "servings": 2,
        "ingredients": [{"name": "Pasta", "amount": "200 g"}, {"name": "Panceta", "amount": "100 g"}],
        "steps": ["Cuece la pasta", "Fríe la panceta", "Mezcla fuera del fuego"],
        "tags": ["italiana"],
    })
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["title"] == "Pasta carbonara"
    assert data["image"] != ""


def test_listar_recetas_incluye_la_creada(client, auth_headers, recipe):
    r = client.get("/api/recipes", headers=auth_headers)
    assert r.status_code == 200
    ids = [x["id"] for x in r.json()]
    assert recipe["id"] in ids


def test_obtener_receta_por_id(client, auth_headers, recipe):
    r = client.get(f"/api/recipes/{recipe['id']}", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == recipe["id"]
    assert data["title"] == recipe["title"]


def test_actualizar_titulo_de_receta(client, auth_headers, recipe):
    r = client.put(f"/api/recipes/{recipe['id']}", headers=auth_headers, json={
        **recipe,
        "title": "Tortilla mejorada",
    })
    assert r.status_code == 200
    assert r.json()["title"] == "Tortilla mejorada"


def test_eliminar_receta(client, auth_headers, recipe):
    r = client.delete(f"/api/recipes/{recipe['id']}", headers=auth_headers)
    assert r.status_code == 204
    r2 = client.get(f"/api/recipes/{recipe['id']}", headers=auth_headers)
    assert r2.status_code == 404


def test_obtener_receta_inexistente_devuelve_404(client, auth_headers):
    r = client.get("/api/recipes/999999", headers=auth_headers)
    assert r.status_code == 404


def test_actualizar_receta_inexistente_devuelve_404(client, auth_headers):
    r = client.put("/api/recipes/999999", headers=auth_headers, json={
        "title": "No existe",
        "description": "",
        "category": "Test",
        "servings": 2,
        "ingredients": [],
        "steps": [],
        "tags": [],
    })
    assert r.status_code == 404


def test_eliminar_receta_inexistente_devuelve_404(client, auth_headers):
    r = client.delete("/api/recipes/999999", headers=auth_headers)
    assert r.status_code == 404


def test_editar_receta_no_resetea_favorito(client, auth_headers, recipe):
    client.post(f"/api/recipes/{recipe['id']}/favorite", headers=auth_headers)

    r = client.put(f"/api/recipes/{recipe['id']}", headers=auth_headers, json={
        **recipe,
        "title": "Título actualizado",
    })
    assert r.status_code == 200

    r2 = client.get(f"/api/recipes/{recipe['id']}", headers=auth_headers)
    assert r2.json()["favorite"] is True
