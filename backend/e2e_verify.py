'''End-to-end pipeline verification: ingest -> detect -> alert -> dashboard.'''

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User

Base.metadata.create_all(bind=engine)
db = SessionLocal()
# seed admin
if not db.query(User).filter(User.username == "e2eadmin").first():
    db.add(User(username="e2eadmin", email="e2e@sentinelx.com",
                password_hash=get_password_hash("E2ePass123!"), role="admin"))
    db.commit()
# seed detection rules
from app.models.detection_rule import DetectionRule
for rule_obj in [
    DetectionRule(name="Brute-force authentication attempts", description="d", mitre_technique_id="T1110",
                  mitre_tactic="Credential Access", severity="high", threshold=5, time_window=300,
                  enabled=True, rule_type="brute_force", config={}),
    DetectionRule(name="Privilege escalation indicators", description="d", mitre_technique_id="T1548",
                  mitre_tactic="Privilege Escalation", severity="high", threshold=1, time_window=300,
                  enabled=True, rule_type="privilege_escalation", config={}),
]:
    if not db.query(DetectionRule).filter(DetectionRule.name == rule_obj.name).first():
        db.add(rule_obj)
db.commit()

client = TestClient(app)
r = client.post("/api/v1/auth/login", json={"username": "e2eadmin", "password": "E2ePass123!"})
assert r.status_code == 200, r.text
token = r.json()["access_token"]
h = {"Authorization": "Bearer " + token}

# 1. Ingest JSON logs (brute force from one IP)
payload = "\n".join([
    '{"timestamp":"2026-01-15T08:15:10Z","source":"linux_auth","hostname":"web-01","username":"root","source_ip":"192.168.1.100","destination_ip":"10.0.0.10","event_type":"login_failure","severity":"medium","description":"Failed password for root from 192.168.1.100","raw_event":{},"event_metadata":{}}',
    '{"timestamp":"2026-01-15T08:15:22Z","source":"linux_auth","hostname":"web-01","username":"root","source_ip":"192.168.1.100","destination_ip":"10.0.0.10","event_type":"login_failure","severity":"medium","description":"Failed password for root from 192.168.1.100","raw_event":{},"event_metadata":{}}',
    '{"timestamp":"2026-01-15T08:15:35Z","source":"linux_auth","hostname":"web-01","username":"root","source_ip":"192.168.1.100","destination_ip":"10.0.0.10","event_type":"login_failure","severity":"medium","description":"Failed password for root from 192.168.1.100","raw_event":{},"event_metadata":{}}',
    '{"timestamp":"2026-01-15T08:15:48Z","source":"linux_auth","hostname":"web-01","username":"root","source_ip":"192.168.1.100","destination_ip":"10.0.0.10","event_type":"login_failure","severity":"medium","description":"Failed password for root from 192.168.1.100","raw_event":{},"event_metadata":{}}',
    '{"timestamp":"2026-01-15T08:16:01Z","source":"linux_auth","hostname":"web-01","username":"root","source_ip":"192.168.1.100","destination_ip":"10.0.0.10","event_type":"login_failure","severity":"medium","description":"Failed password for root from 192.168.1.100","raw_event":{},"event_metadata":{}}',
    '{"timestamp":"2026-01-15T08:17:12Z","source":"linux_auth","hostname":"web-01","username":"charlie","source_ip":"10.0.0.7","destination_ip":"10.0.0.10","event_type":"privilege_escalation","severity":"high","description":"sudo su -","raw_event":{},"event_metadata":{}}',
])
r = client.post("/api/v1/ingestion/upload", files={"file": ("auth.json", payload, "application/json")}, headers=h)
assert r.status_code == 200, r.text
report = r.json()
assert report["accepted"] == 6, report
print("INGESTION:", report["accepted"], "accepted,", report["rejected"], "rejected")

# 2. Run detection evaluation
r = client.post("/api/v1/rules/evaluate", headers=h)
assert r.status_code == 200, r.text
result = r.json()
print("DETECTION:", result["created_alerts"], "alerts created")
assert result["created_alerts"] >= 1, "expected at least one alert"

# 3. Verify alerts created
r = client.get("/api/v1/alerts/", headers=h)
assert r.status_code == 200, r.text
alerts = r.json()["items"]
assert len(alerts) >= 1, "expected alerts"
print("ALERTS:", len(alerts), "total")
for a in alerts:
    print("  -", a["alert_id"], a["title"], "|", a["severity"], "|", a["status"])

# 4. Verify dashboard stats reflect ingested data
r = client.get("/api/v1/dashboard/stats", headers=h)
assert r.status_code == 200, r.text
stats = r.json()
print("DASHBOARD:", stats)
assert stats["total_events"] == 6, stats

# 5. Verify events list
r = client.get("/api/v1/events/", headers=h)
assert r.status_code == 200, r.text
assert r.json()["total"] == 6

print("\nEND-TO-END PIPELINE VERIFIED")
db.close()
Base.metadata.drop_all(bind=engine)
