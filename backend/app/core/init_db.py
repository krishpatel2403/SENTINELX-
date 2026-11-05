"""Database initialization: create tables and seed default data.

Run with: `python -m app.core.init_db` from the backend directory.
"""

from app.core.database import engine, SessionLocal, Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.detection_rule import DetectionRule
import logging

logger = logging.getLogger("sentinelx")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

    db = SessionLocal()
    try:
        # Seed default admin user if absent.
        admin = db.query(User).filter(User.username == settings.SEED_ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=settings.SEED_ADMIN_USERNAME,
                email=settings.SEED_ADMIN_EMAIL,
                password_hash=get_password_hash(settings.SEED_ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info(f"Seeded admin user: {settings.SEED_ADMIN_USERNAME}")

        # Seed default detection rules if absent.
        default_rules = [
            DetectionRule(
                name="Brute-force authentication attempts",
                description="Detects repeated authentication failures from a single source IP within a time window.",
                mitre_technique_id="T1110",
                mitre_tactic="Credential Access",
                severity="high",
                threshold=5,
                time_window=300,
                enabled=True,
                rule_type="brute_force",
                config={},
            ),
            DetectionRule(
                name="Repeated failed logins",
                description="Detects repeated failed login events for a single user account.",
                mitre_technique_id="T1110",
                mitre_tactic="Credential Access",
                severity="medium",
                threshold=5,
                time_window=300,
                enabled=True,
                rule_type="failed_login",
                config={},
            ),
            DetectionRule(
                name="Privilege escalation indicators",
                description="Detects sudo/su or admin-group modification events indicating privilege escalation.",
                mitre_technique_id="T1548",
                mitre_tactic="Privilege Escalation",
                severity="high",
                threshold=1,
                time_window=300,
                enabled=True,
                rule_type="privilege_escalation",
                config={},
            ),
            DetectionRule(
                name="Unusual administrative activity",
                description="Detects administrative actions outside typical patterns or from unusual sources.",
                mitre_technique_id="T1078",
                mitre_tactic="Defense Evasion",
                severity="medium",
                threshold=3,
                time_window=300,
                enabled=True,
                rule_type="admin_activity",
                config={},
            ),
            DetectionRule(
                name="Repeated access-denied events",
                description="Detects repeated access-denied events from a single source, indicating probing.",
                mitre_technique_id="T1210",
                mitre_tactic="Discovery",
                severity="medium",
                threshold=5,
                time_window=300,
                enabled=True,
                rule_type="access_denied",
                config={},
            ),
            DetectionRule(
                name="Suspicious process execution indicators",
                description="Detects execution of known suspicious processes or scripts.",
                mitre_technique_id="T1059",
                mitre_tactic="Execution",
                severity="high",
                threshold=1,
                time_window=300,
                enabled=True,
                rule_type="suspicious_process",
                config={},
            ),
            DetectionRule(
                name="Known malicious IOC matches",
                description="Matches events against known malicious indicators of compromise.",
                mitre_technique_id="T1071",
                mitre_tactic="Command and Control",
                severity="critical",
                threshold=1,
                time_window=300,
                enabled=True,
                rule_type="ioc_match",
                config={},
            ),
            DetectionRule(
                name="Unusual event frequency",
                description="Detects abnormally high event frequency from a single source.",
                mitre_technique_id="T1499",
                mitre_tactic="Impact",
                severity="medium",
                threshold=100,
                time_window=300,
                enabled=True,
                rule_type="frequency",
                config={},
            ),
            DetectionRule(
                name="Multiple security failures from one source",
                description="Detects multiple security failure event types originating from a single source IP.",
                mitre_technique_id="T1110",
                mitre_tactic="Credential Access",
                severity="high",
                threshold=3,
                time_window=300,
                enabled=True,
                rule_type="multi_failure",
                config={},
            ),
        ]
        for rule in default_rules:
            exists = db.query(DetectionRule).filter(DetectionRule.name == rule.name).first()
            if not exists:
                db.add(rule)
        db.commit()
        logger.info("Default detection rules seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    print("Database initialization complete.")
