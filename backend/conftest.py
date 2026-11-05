"""Pytest fixtures for SentinelX backend tests.

A dedicated SQLite test database is used so tests never touch the dev DB.
The TestClient shares the same transactional session as the test (via a
``get_db`` dependency override), so data created in fixtures is visible to
requests and rolled back after each test for isolation.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_sentinelx.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.api.deps import get_db as api_get_db
from app.main import app
from app.core.security import get_password_hash
from app.models.user import User


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("test_sentinelx.db")
    except OSError:
        pass


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    """TestClient whose get_db dependency uses the test's transactional session."""

    def _override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[api_get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db: Session) -> User:
    user = User(
        username="admin",
        email="admin@sentinelx.com",
        password_hash=get_password_hash("AdminPass123!"),
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture()
def analyst_user(db: Session) -> User:
    user = User(
        username="analyst",
        email="analyst@sentinelx.com",
        password_hash=get_password_hash("AnalystPass123!"),
        role="analyst",
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture()
def auth_headers(client: TestClient, admin_user: User):
    r = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "AdminPass123!"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
