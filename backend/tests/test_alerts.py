'''Alert management API tests.'''

from datetime import datetime, timezone, timedelta


def _seed_rule_and_event(db):
    from app.models.detection_rule import DetectionRule
    from app.models.security_event import SecurityEvent
    rule = DetectionRule(
        name="Test Detect Rule", description="d", severity="high",
        threshold=1, time_window=300, enabled=True, rule_type="brute_force", config={},
    )
    db.add(rule)
    db.flush()
    ts = datetime.now(timezone.utc) - timedelta(minutes=1)
    event = SecurityEvent(
        event_id="alert-evt-1", timestamp=ts, source="linux_auth",
        hostname="h", username="u", source_ip="10.0.0.1",
        destination_ip="10.0.0.2", event_type="login_failure",
        severity="high", description="failed login", raw_event={}, event_metadata={},
    )
    db.add(event)
    db.flush()
    return rule, event


def test_create_alert(client, auth_headers, db):
    rule, event = _seed_rule_and_event(db)
    r = client.post("/api/v1/alerts/", headers=auth_headers, json={
        "rule_id": rule.id,
        "event_id": event.id,
        "title": "Test Alert",
        "description": "A test alert",
        "severity": "high",
        "status": "new",
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["title"] == "Test Alert"
    assert body["status"] == "new"


def test_list_alerts(client, auth_headers, db):
    rule, event = _seed_rule_and_event(db)
    from app.services import alerts as alert_service
    alert_service.create_alert(db, rule.id, event.id, "A", "B", "high", "new")
    db.commit()
    r = client.get("/api/v1/alerts/", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1


def test_get_alert(client, auth_headers, db):
    rule, event = _seed_rule_and_event(db)
    from app.services import alerts as alert_service
    alert = alert_service.create_alert(db, rule.id, event.id, "A", "B", "high", "new")
    db.commit()
    r = client.get("/api/v1/alerts/" + str(alert.id), headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == alert.id


def test_update_alert_status(client, auth_headers, db):
    rule, event = _seed_rule_and_event(db)
    from app.services import alerts as alert_service
    alert = alert_service.create_alert(db, rule.id, event.id, "A", "B", "high", "new")
    db.commit()
    r = client.patch("/api/v1/alerts/" + str(alert.id), headers=auth_headers, json={
        "status": "investigating",
        "assigned_to": 1,
    })
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "investigating"


def test_alerts_require_auth(client):
    r = client.get("/api/v1/alerts/")
    assert r.status_code == 401
