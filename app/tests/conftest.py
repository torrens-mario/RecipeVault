import os
import sys
import uuid
import pytest
from pathlib import Path

# Patch JSONB -> JSON before any app module is imported so SQLite works in tests
from sqlalchemy.types import JSON
import sqlalchemy.dialects.postgresql as _pg
_pg.JSONB = JSON

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_recipevault.db")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing")
os.environ.setdefault("BLOB_ACCOUNT_URL", "https://test.blob.core.windows.net")
os.environ.setdefault("BLOB_CONTAINER", "test-container")

sys.path.insert(0, str(Path(__file__).parent.parent))

import database as _db


def _patch_engine():
    """Replace engine factory with SQLite-compatible version."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    if _db._engine is None:
        _db._engine = create_engine(
            os.environ["DATABASE_URL"],
            connect_args={"check_same_thread": False},
        )
        _db._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_db._engine)
    return _db._engine


_db._get_engine = _patch_engine


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    _db.init_db()
    yield
    if _db._engine is not None:
        _db._engine.dispose()
    _db._engine = None
    db_file = Path("test_recipevault.db")
    try:
        db_file.unlink(missing_ok=True)
    except PermissionError:
        pass


@pytest.fixture(scope="session")
def client(_setup_db):
    from app import app
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c


@pytest.fixture
def new_user(client):
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"user_{suffix}",
        "email": f"user_{suffix}@test.com",
        "password": "testpass123",
    }
    r = client.post("/api/auth/register", json=payload)
    return {**payload, **r.json()}


@pytest.fixture
def auth_headers(new_user):
    return {"Authorization": f"Bearer {new_user['access_token']}"}


@pytest.fixture
def recipe(client, auth_headers):
    suffix = uuid.uuid4().hex[:6]
    r = client.post("/api/recipes", headers=auth_headers, json={
        "title": f"Tortilla_{suffix}",
        "description": "Receta de prueba",
        "category": "Española",
        "servings": 4,
        "ingredients": [{"name": "Huevos", "amount": "6 uds"}, {"name": "Patata", "amount": "500 g"}],
        "steps": ["Fríe las patatas", "Mezcla con huevo y cuaja"],
        "tags": ["test"],
    })
    assert r.status_code == 201
    return r.json()
