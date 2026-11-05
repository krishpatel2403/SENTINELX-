'''Threat intelligence and MITRE ATT&CK tests.'''


def test_enrich_unknown_indicator_is_not_clean(client, auth_headers, db):
    r = client.get(
        "/api/v1/intelligence/enrich/ip/1.2.3.4", headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["available"] is False
    assert body["classification"] == "unknown"
    assert body["source"] == "none"
    assert body["confidence"] is None


def test_enrich_malicious_indicator(client, auth_headers, db):
    from app.intelligence.service import IntelligenceService
    svc = IntelligenceService(db)
    svc.upsert_indicator("ip", "1.2.3.4", classification="malicious",
                         reputation="bad", source="local", confidence=90)
    db.commit()
    r = client.get(
        "/api/v1/intelligence/enrich/ip/1.2.3.4", headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["available"] is True
    assert body["classification"] == "malicious"
    assert body["confidence"] == 90


def test_enrich_benign_is_clean_not_unknown(client, auth_headers, db):
    from app.intelligence.service import IntelligenceService
    svc = IntelligenceService(db)
    svc.upsert_indicator("ip", "9.9.9.9", classification="benign",
                         reputation="clean", source="local", confidence=99)
    db.commit()
    r = client.get(
        "/api/v1/intelligence/enrich/ip/9.9.9.9", headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["available"] is True
    assert body["classification"] == "benign"


def test_list_indicators(client, auth_headers, db):
    from app.intelligence.service import IntelligenceService
    svc = IntelligenceService(db)
    svc.upsert_indicator("domain", "evil.example.com", classification="malicious",
                         source="local", confidence=80)
    db.commit()
    r = client.get("/api/v1/intelligence/indicators", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1


def test_intelligence_requires_auth(client):
    r = client.get("/api/v1/intelligence/enrich/ip/1.2.3.4")
    assert r.status_code == 401


def test_mitre_techniques(client, auth_headers):
    r = client.get("/api/v1/mitre/techniques", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    ids = {t["technique_id"] for t in body}
    assert "T1110" in ids
    assert "T1548" in ids
    assert "T1059" in ids


def test_mitre_mapping(client, auth_headers, db):
    from app.models.detection_rule import DetectionRule
    rule = DetectionRule(
        name="MITRE Test Rule", description="d", severity="medium",
        threshold=1, time_window=300, enabled=True, rule_type="brute_force", config={},
    )
    db.add(rule)
    db.flush()
    r = client.get("/api/v1/mitre/mapping", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    rule_map = {m["rule_name"]: m for m in body["rule_mapping"]}
    assert "MITRE Test Rule" in rule_map
    assert rule_map["MITRE Test Rule"]["technique"]["technique_id"] == "T1110"
