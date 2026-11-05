"""Security events API tests."""


def test_events_list(client, auth_headers):
    r = client.get("/api/v1/events/", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "total" in body


def test_events_summary(client, auth_headers):
    r = client.get("/api/v1/events/stats/summary", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "total_events" in body
    assert "by_severity" in body


def test_events_requires_auth(client):
    r = client.get("/api/v1/events/")
    assert r.status_code == 401
