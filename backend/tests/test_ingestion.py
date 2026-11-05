"""Ingestion API and service tests."""

import json


def test_syslog_parser(client, db):
    from app.ingestion.parser import parse_syslog_line
    line = "Jan 10 08:12:31 myhost sshd[1234]: Failed password for root from 192.168.1.50 port 22 ssh2"
    event, reason = parse_syslog_line(line, "linux_auth")
    assert reason is None
    assert event["event_type"] == "login_failure"
    assert event["severity"] == "medium"
    assert event["source_ip"] == "192.168.1.50"
    assert event["username"] == "root"
    assert event["hostname"] == "myhost"
    assert event["timestamp"] is not None


def test_json_record_parser(client, db):
    from app.ingestion.parser import parse_json_record
    line = json.dumps({
        "timestamp": "2026-01-01T10:00:00Z",
        "source": "json",
        "username": "alice",
        "source_ip": "10.0.0.1",
        "event_type": "login",
        "severity": "low",
        "description": "test",
    })
    event, reason = parse_json_record(line, "json")
    assert reason is None
    assert event["username"] == "alice"
    assert event["timestamp"] is not None


def test_malformed_json_rejected(client, db):
    from app.ingestion.parser import parse_json_record
    event, reason = parse_json_record("{not valid json", "json")
    assert reason is not None
    assert event["event_id"] is None


def test_csv_row_parser(client, db):
    from app.ingestion.parser import parse_csv_record
    row = {
        "timestamp": "2026-01-01T10:00:00Z",
        "source_ip": "10.0.0.2",
        "username": "bob",
        "event_type": "login_failure",
        "severity": "medium",
        "description": "csv test",
    }
    event, reason = parse_csv_record(row, "csv")
    assert reason is None
    assert event["username"] == "bob"
    assert event["source_ip"] == "10.0.0.2"


def test_ingestion_upload_json_lines(client, auth_headers):
    payload = (
        '{"timestamp":"2026-01-01T10:00:00Z","username":"alice","source_ip":"10.0.0.1",'
        '"event_type":"login","severity":"low","description":"ok"}\n'
        '{bad json}\n'
        '{"timestamp":"2026-01-01T10:01:00Z","username":"bob","source_ip":"10.0.0.2",'
        '"event_type":"login_failure","severity":"medium","description":"fail"}\n'
    )
    r = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("auth.json", payload, "application/json")},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    report = r.json()
    assert report["accepted"] == 2
    assert report["rejected"] == 1
    assert report["total_records"] == 3
    # Check the rejected record has a reason.
    rejected = [x for x in report["results"] if not x["accepted"]]
    assert len(rejected) == 1
    assert rejected[0]["reason"] is not None


def test_ingestion_upload_csv(client, auth_headers):
    payload = "timestamp,source_ip,username,event_type,severity,description\n"
    payload += "2026-01-01T10:00:00Z,10.0.0.1,alice,login,low,csv login\n"
    r = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("events.csv", payload, "text/csv")},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    report = r.json()
    assert report["accepted"] == 1
    assert report["total_records"] == 1


def test_ingestion_supported_sources(client, auth_headers):
    r = client.get("/api/v1/ingestion/sources", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    ids = [s["id"] for s in body["sources"]]
    assert "linux_auth" in ids
    assert "json" in ids
    assert "csv" in ids


def test_ingestion_requires_auth(client):
    r = client.post("/api/v1/ingestion/upload", files={"file": ("x.txt", b"hi", "text/plain")})
    assert r.status_code == 401
