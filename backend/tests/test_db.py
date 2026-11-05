"""Database model smoke tests."""


def test_tables_exist(prepare_database):
    from app.core.database import engine
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected = {"users", "security_events", "detection_rules", "alerts", "incidents",
                "incident_notes", "incident_alerts", "threat_indicators", "audit_logs",
                "report_records"}
    for t in expected:
        assert t in tables, f"missing table {t}"


def test_user_can_be_created_and_queried(prepare_database, db):
    from app.models.user import User
    from app.core.security import get_password_hash
    user = User(
        username="seedme",
        email="seedme@sentinelx.com",
        password_hash=get_password_hash("Pass123!"),
        role="analyst",
        is_active=True,
    )
    db.add(user)
    db.flush()
    found = db.query(User).filter(User.username == "seedme").first()
    assert found is not None
    assert found.role == "analyst"
