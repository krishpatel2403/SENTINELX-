'''Detection engine and rules API tests.'''

from datetime import datetime, timezone, timedelta

_counter = [0]


def _next_id():
    _counter[0] += 1
    return _counter[0]


def _make_event(db, source_ip, event_type, severity, description, minutes_ago=1, username="alice"):
    from app.models.security_event import SecurityEvent
    ts = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    e = SecurityEvent(
        event_id="det-evt-" + str(_next_id()) + "-" + source_ip + "-" + event_type,
        timestamp=ts,
        source="linux_auth",
        hostname="host1",
        username=username,
        source_ip=source_ip,
        destination_ip="10.0.0.2",
        event_type=event_type,
        severity=severity,
        description=description,
        raw_event={"line": description},
        event_metadata={},
    )
    db.add(e)
    db.flush()
    return e


def _seed_brute_force_rule(db):
    from app.models.detection_rule import DetectionRule
    rule = DetectionRule(
        name="Brute-force authentication attempts",
        description="Repeated authentication failures from a single source IP.",
        mitre_technique_id="T1110",
        mitre_tactic="Credential Access",
        severity="high",
        threshold=5,
        time_window=300,
        enabled=True,
        rule_type="brute_force",
        config={},
    )
    db.add(rule)
    db.flush()
    return rule


def test_engine_brute_force_creates_alert(client, db, admin_user, auth_headers):
    from app.detection.engine import DetectionEngine
    rule = _seed_brute_force_rule(db)
    for i in range(6):
        _make_event(db, "10.0.0.99", "login_failure", "medium",
                    "Failed password for root from 10.0.0.99", minutes_ago=1)
    db.flush()
    engine = DetectionEngine(db)
    created = engine.evaluate_all()
    db.commit()
    assert len(created) >= 1, "expected at least one brute-force alert"
    assert any(a.severity == "high" for a in created)
    assert any(a.rule_id == rule.id for a in created)


def test_engine_no_events_no_alerts(client, db, auth_headers):
    from app.detection.engine import DetectionEngine
    engine = DetectionEngine(db)
    created = engine.evaluate_all()
    assert created == []


def test_disable_rule_stops_alerts(client, db, admin_user, auth_headers):
    from app.models.detection_rule import DetectionRule
    from app.detection.engine import DetectionEngine
    rule = _seed_brute_force_rule(db)
    # Unique usernames so failed_login (threshold 5 per user) does not fire.
    for i in range(6):
        _make_event(db, "10.0.0.99", "login_failure", "medium",
                    "Failed password for user" + str(i) + " from 10.0.0.99",
                    minutes_ago=1, username="user" + str(i))
    db.flush()
    rule.enabled = False
    db.commit()
    engine = DetectionEngine(db)
    created = engine.evaluate_all()
    db.commit()
    assert not any(a.rule_id == rule.id for a in created), \
        "disabled rule must not create alerts"


def test_evaluate_api(client, auth_headers):
    r = client.post("/api/v1/rules/evaluate", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "created_alerts" in body
    assert body["created_alerts"] == 0  # no events seeded


def test_rule_crud(client, auth_headers):
    r = client.post("/api/v1/rules/", headers=auth_headers, json={
        "name": "Test Rule",
        "description": "A test detection rule",
        "severity": "low",
        "threshold": 3,
        "time_window": 300,
        "enabled": True,
        "rule_type": "frequency",
        "config": {},
    })
    assert r.status_code == 201, r.text
    rule_id = r.json()["id"]
    r = client.get("/api/v1/rules/", headers=auth_headers)
    assert r.status_code == 200
    assert any(x["id"] == rule_id for x in r.json())
    r = client.patch("/api/v1/rules/" + str(rule_id), headers=auth_headers, json={
        "enabled": False,
    })
    assert r.status_code == 200
    assert r.json()["enabled"] is False
    r = client.delete("/api/v1/rules/" + str(rule_id), headers=auth_headers)
    assert r.status_code == 204
    r = client.get("/api/v1/rules/" + str(rule_id), headers=auth_headers)
    assert r.status_code == 404
