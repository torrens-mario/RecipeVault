"""
Tests para la lógica de cocinar una receta (POST /api/recipes/{id}/cook):
- descuenta ingredientes del inventario cuando hay stock suficiente
- rechaza si falta algún ingrediente
- rechaza si el stock es insuficiente
"""


def _crear_receta(client, auth_headers, ingredientes):
    r = client.post("/api/recipes", headers=auth_headers, json={
        "title": "Receta de prueba cook",
        "description": "",
        "category": "Test",
        "servings": 2,
        "ingredients": ingredientes,
        "steps": ["Paso único"],
        "tags": [],
    })
    assert r.status_code == 201
    return r.json()


def _crear_item(client, auth_headers, name, quantity, unit):
    r = client.post("/api/inventory", headers=auth_headers, json={
        "name": name,
        "quantity": quantity,
        "unit": unit,
        "low_stock_threshold": 0,
        "low_stock_unit": unit,
    })
    assert r.status_code == 201
    return r.json()


def test_cocinar_descuenta_inventario(client, auth_headers):
    _crear_item(client, auth_headers, "Almidón de tapioca", 500, "g")
    receta = _crear_receta(client, auth_headers, [{"name": "Almidón de tapioca", "amount": "200 g"}])

    r = client.post(f"/api/recipes/{receta['id']}/cook", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True

    item = next(i for i in data["inventory"] if i["name"] == "Almidón de tapioca")
    assert item["quantity"] == 300


def test_cocinar_falla_sin_ingrediente_en_inventario(client, auth_headers):
    receta = _crear_receta(client, auth_headers, [{"name": "Trufa negra", "amount": "50 g"}])

    r = client.post(f"/api/recipes/{receta['id']}/cook", headers=auth_headers)
    assert r.status_code == 400
    data = r.json()
    assert data["success"] is False
    assert any(m["name"] == "Trufa negra" for m in data["missing"])


def test_cocinar_falla_con_stock_insuficiente(client, auth_headers):
    _crear_item(client, auth_headers, "Bebida de almendras", 100, "ml")
    receta = _crear_receta(client, auth_headers, [{"name": "Bebida de almendras", "amount": "500 ml"}])

    r = client.post(f"/api/recipes/{receta['id']}/cook", headers=auth_headers)
    assert r.status_code == 400
    data = r.json()
    assert data["success"] is False
    assert any(m["name"] == "Bebida de almendras" for m in data["missing"])


def test_cocinar_no_descuenta_si_falta_alguno(client, auth_headers):
    """Si falta UN ingrediente, no se descuenta NINGUNO (operación atómica)."""
    item = _crear_item(client, auth_headers, "Almidón de maíz", 500, "g")
    receta = _crear_receta(client, auth_headers, [
        {"name": "Almidón de maíz", "amount": "200 g"},
        {"name": "Levadura espacial", "amount": "10 g"},  # no existe en inventario
    ])

    r = client.post(f"/api/recipes/{receta['id']}/cook", headers=auth_headers)
    assert r.status_code == 400

    # El almidón no debe haberse descontado
    inventario = client.get("/api/inventory", headers=auth_headers).json()
    almid = next(i for i in inventario if i["id"] == item["id"])
    assert almid["quantity"] == 500


def test_cocinar_receta_inexistente_devuelve_404(client, auth_headers):
    r = client.post("/api/recipes/999999/cook", headers=auth_headers)
    assert r.status_code == 404


def test_cocinar_convierte_unidades(client, auth_headers):
    """1500 g en inventario, receta necesita 1 kg → debe quedar 500 g."""
    _crear_item(client, auth_headers, "Lentejas rojas", 1500, "g")
    receta = _crear_receta(client, auth_headers, [{"name": "Lentejas rojas", "amount": "1 kg"}])

    r = client.post(f"/api/recipes/{receta['id']}/cook", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True

    item = next(i for i in data["inventory"] if i["name"] == "Lentejas rojas")
    assert item["quantity"] == 500
