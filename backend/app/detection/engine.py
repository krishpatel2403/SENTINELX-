'''Detection engine: evaluates enabled detection rules against normalized events.

When a rule matches, an Alert is created. Alerts are de-duplicated so the same
rule + match key does not generate a new alert on every evaluation run.
'''

from __future__ import annotations

import hashlib
from datetime import timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.detection_rule import DetectionRule
from app.models.security_event import SecurityEvent
from app.detection.evaluators import RULE_EVALUATORS


class DetectionEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_enabled_rules(self) -> List[DetectionRule]:
        return (
            self.db.query(DetectionRule)
            .filter(DetectionRule.enabled == True)  # noqa: E712
            .all()
        )

    def evaluate_all(self) -> List[Alert]:
        '''Evaluate every enabled rule and create alerts for new matches.'''
        rules = self.get_enabled_rules()
        if not rules:
            return []

        max_window = max((r.time_window or 300) for r in rules)
        events = (
            self.db.query(SecurityEvent)
            .filter(SecurityEvent.timestamp.isnot(None))
            .all()
        )
        # Restrict to events within the largest time window for efficiency.
        if events:
            latest = max((e.timestamp for e in events if e.timestamp), default=None)
            if latest:
                cutoff = latest - timedelta(seconds=max_window)
                events = [e for e in events if e.timestamp and e.timestamp >= cutoff]

        created: List[Alert] = []
        for rule in rules:
            evaluator = RULE_EVALUATORS.get(rule.rule_type)
            if not evaluator:
                continue
            matches = evaluator(rule, events, self.db)
            for match in matches:
                alert = self._create_alert_if_new(rule, match)
                if alert:
                    created.append(alert)
        return created

    def _create_alert_if_new(self, rule: DetectionRule,
                             match: Dict[str, Any]) -> Optional[Alert]:
        alert_id = "alert:" + hashlib.sha256(
            (str(rule.id) + ":" + match["key"]).encode()).hexdigest()[:24]
        existing = self.db.query(Alert).filter(Alert.alert_id == alert_id).first()
        if existing:
            return None
        matched_ids = match.get("matched_event_ids") or []
        primary_event = None
        if matched_ids:
            primary_event = (
                self.db.query(SecurityEvent)
                .filter(SecurityEvent.id == matched_ids[0])
                .first()
            )
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.id,
            event_id=primary_event.id if primary_event else 0,
            title=rule.name,
            description=match.get("description", rule.description),
            severity=rule.severity,
            status="new",
            assigned_to=None,
        )
        # Fallback: if no primary event, pick the earliest matched event.
        if not primary_event and matched_ids:
            first = (
                self.db.query(SecurityEvent)
                .filter(SecurityEvent.id.in_(matched_ids))
                .order_by(SecurityEvent.timestamp.asc())
                .first()
            )
            if first:
                alert.event_id = first.id
        self.db.add(alert)
        self.db.flush()
        return alert
