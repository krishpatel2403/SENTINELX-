'''Incident management API tests.'''


def _seed_alert(db):
    from app.models.detection_rule import DetectionRule
    from app.models.security_event import SecurityEvent
    from app.services import alerts as alert_service
    rule = DetectionRule(
        name="Incident Test Rule", description="d", severity="high",
        threshold=1, time_window=300, enabled=True, rule_type="brute_force", config={},
    )
    db.add(rule)
    db.flush()
    from datetime import datetime, timezone, timedelta
    ts = datetime.now(timezone.utc) - timedelta(minutes=1)
    event = SecurityEvent(
        event_id="inc-evt-1", timestamp=ts, source="linux_auth",
        hostname="h", username="u", source_ip="10.0.0.1",
        destination_ip="10.0.0.2", event_type="login_failure",
        severity="high", description="failed login", raw_event={}, event_metadata={},
    )
    db.add(event)
    db.flush()
    return alert_service.create_alert(db, rule.id, event.id, "Inc Alert", "d", "high", "new")


def test_create_incident(client, auth_headers, db):
    alert = _seed_alert(db)
    db.commit()
    r = client.post("/api/v1/incidents/", headers=auth_headers, json={
        "title": "Test Incident",
        "description": "A test incident",
        "severity": "high",
        "status": "detection",
        "alert_ids": [alert.id],
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["title"] == "Test Incident"
    assert body["status"] == "detection"


def test_list_incidents(client, auth_headers, db):
    from app.services import incidents as incident_service
    incident_service.create_incident(db, "T", "D", "high", "detection")
    db.commit()
    r = client.get("/api/v1/incidents/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_incident_lifecycle(client, auth_headers, db):
    from app.services import incidents as incident_service
    inc = incident_service.create_incident(db, "LC", "desc", "high", "detection")
    db.commit()
    # valid transition detection -> triage
    r = client.patch("/api/v1/incidents/" + str(inc.id), headers=auth_headers, json={
        "status": "triage",
    })
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "triage"
    # invalid transition triage -> closure
    r = client.patch("/api/v1/incidents/" + str(inc.id), headers=auth_headers, json={
        "status": "closure",
    })
    assert r.status_code == 400, r.text


def test_add_incident_note(client, auth_headers, db):
    from app.services import incidents as incident_service
    inc = incident_service.create_incident(db, "Note", "desc", "medium", "detection")
    db.commit()
    r = client.post("/api/v1/incidents/" + str(inc.id) + "/notes", headers=auth_headers, json={
        "note": "Investigating this incident",
    })
    assert r.status_code == 201, r.text
    assert r.json()["note"] == "Investigating this incident"


def test_incidents_require_auth(client):
    r = client.get("/api/v1/incidents/")
    assert r.status_code == 401
