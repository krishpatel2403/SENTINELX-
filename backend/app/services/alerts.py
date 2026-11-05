'''Alert management service.'''

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.models.security_event import SecurityEvent
from app.models.user import User


def list_alerts(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> Tuple[List[Alert], int]:
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    if assigned_to is not None:
        query = query.filter(Alert.assigned_to == assigned_to)
    if search:
        like = "%" + search + "%"
        query = query.filter(
            (Alert.title.like(like)) | (Alert.description.like(like))
        )
    total = query.count()
    items = (
        query.order_by(Alert.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    return db.query(Alert).filter(Alert.id == alert_id).first()


def create_alert(
    db: Session,
    rule_id: int,
    event_id: int,
    title: str,
    description: str,
    severity: str,
    status: str = "new",
    assigned_to: Optional[int] = None,
) -> Alert:
    alert_id = "alert:" + hashlib.sha256(
        (str(rule_id) + ":" + str(event_id) + ":" + str(datetime.now(timezone.utc).timestamp())).encode()
    ).hexdigest()[:24]
    alert = Alert(
        alert_id=alert_id,
        rule_id=rule_id,
        event_id=event_id,
        title=title,
        description=description,
        severity=severity,
        status=status,
        assigned_to=assigned_to,
    )
    db.add(alert)
    db.flush()
    return alert


def update_alert(
    db: Session,
    alert: Alert,
    title: Optional[str] = None,
    description: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
) -> Alert:
    if title is not None:
        alert.title = title
    if description is not None:
        alert.description = description
    if severity is not None:
        alert.severity = severity
    if status is not None:
        alert.status = status
        if status in ("resolved", "false_positive"):
            alert.resolved_at = datetime.now(timezone.utc)
        else:
            alert.resolved_at = None
    if assigned_to is not None:
        alert.assigned_to = assigned_to
    db.add(alert)
    db.flush()
    return alert


def audit(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    details: dict,
    ip_address: Optional[str] = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)
    db.flush()
    return entry
