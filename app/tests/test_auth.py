import uuid
import pytest
from auth import create_access_token, hash_password, verify_password


# ── Unit tests ────────────────────────────────────────────────────────────────

def test_hash_password_is_not_plaintext():
    hashed = hash_password("micontraseña123")
    assert hashed != "micontraseña123"
    assert len(hashed) > 20


def test_verify_password_correct():
    hashed = hash_password("micontraseña123")
    assert verify_password("micontraseña123", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("micontraseña123")
    assert verify_password("otracontraseña", hashed) is False


# ── Integration tests ─────────────────────────────────────────────────────────

def test_register_creates_user(client):
    suffix = uuid.uuid4().hex[:8]
    r = client.post("/api/auth/register", json={
        "username": f"nuevouser_{suffix}",
        "email": f"nuevouser_{suffix}@test.com",
        "password": "pass1234",
    })
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    assert "nuevouser" in data["username"]


def test_login_success(client, new_user):
    r = client.post("/api/auth/login", json={
        "email": new_user["email"],
        "password": new_user["password"],
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client, new_user):
    r = client.post("/api/auth/login", json={
        "email": new_user["email"],
        "password": "contraseñaincorrecta",
    })
    assert r.status_code == 401
