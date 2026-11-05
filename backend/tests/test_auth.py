"""Authentication API tests."""


def test_login_success(client, admin_user):
    r = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "AdminPass123!"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    assert "password_hash" not in body


def test_login_wrong_password(client, admin_user):
    r = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert r.status_code == 401


def test_login_inactive_user(client, db, admin_user):
    admin_user.is_active = False
    db.flush()
    r = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "AdminPass123!"},
    )
    assert r.status_code == 403


def test_me_requires_auth(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_me_returns_profile(client, auth_headers):
    r = client.get("/api/v1/auth/me", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "admin"
    assert body["role"] == "admin"
    assert "password_hash" not in body


def test_register_admin_only(client, auth_headers):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newadmin",
            "email": "newadmin@sentinelx.com",
            "password": "NewAdmin123!",
            "role": "admin",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text


def test_register_duplicate(client, auth_headers, admin_user):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "username": "admin",
            "email": "other@sentinelx.com",
            "password": "DupPass123!",
            "role": "analyst",
        },
        headers=auth_headers,
    )
    assert r.status_code == 400
