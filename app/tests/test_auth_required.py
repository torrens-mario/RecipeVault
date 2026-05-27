"""
Tests que verifican que los endpoints protegidos rechazan peticiones
sin token (403) o con token inválido (401).
"""


PROTECTED_GET = [
    "/api/recipes",
    "/api/recipes/1",
    "/api/inventory",
    "/api/inventory/low-stock",
    "/api/shopping-list",
    "/api/auth/me",
]

PROTECTED_POST = [
    "/api/recipes",
    "/api/recipes/1/favorite",
    "/api/recipes/1/plan",
    "/api/recipes/1/public",
    "/api/recipes/1/cook",
    "/api/inventory",
]

PROTECTED_PUT = [
    "/api/recipes/1",
    "/api/inventory/1",
]

PROTECTED_DELETE = [
    "/api/recipes/1",
    "/api/inventory/1",
]


def test_sin_token_devuelve_403(client):
    for url in PROTECTED_GET:
        r = client.get(url)
        assert r.status_code == 403, f"GET {url} debería devolver 403 sin token, devolvió {r.status_code}"

    for url in PROTECTED_POST:
        r = client.post(url, json={})
        assert r.status_code == 403, f"POST {url} debería devolver 403 sin token, devolvió {r.status_code}"

    for url in PROTECTED_PUT:
        r = client.put(url, json={})
        assert r.status_code == 403, f"PUT {url} debería devolver 403 sin token, devolvió {r.status_code}"

    for url in PROTECTED_DELETE:
        r = client.delete(url)
        assert r.status_code == 403, f"DELETE {url} debería devolver 403 sin token, devolvió {r.status_code}"


def test_token_invalido_devuelve_401(client):
    headers = {"Authorization": "Bearer tokeninvalido"}

    for url in PROTECTED_GET:
        r = client.get(url, headers=headers)
        assert r.status_code == 401, f"GET {url} debería devolver 401 con token inválido, devolvió {r.status_code}"

    for url in PROTECTED_POST:
        r = client.post(url, json={}, headers=headers)
        assert r.status_code == 401, f"POST {url} debería devolver 401 con token inválido, devolvió {r.status_code}"

    for url in PROTECTED_PUT:
        r = client.put(url, json={}, headers=headers)
        assert r.status_code == 401, f"PUT {url} debería devolver 401 con token inválido, devolvió {r.status_code}"

    for url in PROTECTED_DELETE:
        r = client.delete(url, headers=headers)
        assert r.status_code == 401, f"DELETE {url} debería devolver 401 con token inválido, devolvió {r.status_code}"
