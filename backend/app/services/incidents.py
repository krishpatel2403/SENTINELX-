'''Incident management service.'''

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.models.incident_note import IncidentNote
from app.models.user import User


VALID_TRANSITIONS = {
    "detection": ["triage"],
    "triage": ["investigation"],
    "investigation": ["containment"],
    "containment": ["recovery"],
    "recovery": ["closure"],
}


def list_incidents(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> Tuple[List[Incident], int]:
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if assigned_to is not None:
        query = query.filter(Incident.assigned_to == assigned_to)
    if search:
        like = "%" + search + "%"
        query = query.filter(
            (Incident.title.like(like)) | (Incident.description.like(like))
        )
    total = query.count()
    items = (
        query.order_by(Incident.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_incident(db: Session, incident_id: int) -> Optional[Incident]:
    return db.query(Incident).filter(Incident.id == incident_id).first()


def create_incident(
    db: Session,
    title: str,
    description: str,
    severity: str,
    status: str = "detection",
    assigned_to: Optional[int] = None,
    alert_ids: Optional[List[int]] = None,
) -> Incident:
    incident_id = "incident:" + hashlib.sha256(
        (title + ":" + str(datetime.now(timezone.utc).timestamp())).encode()
    ).hexdigest()[:24]
    incident = Incident(
        incident_id=incident_id,
        title=title,
        description=description,
        severity=severity,
        status=status,
        assigned_to=assigned_to,
    )
    db.add(incident)
    db.flush()
    if alert_ids:
        alerts = (
            db.query(Alert)
            .filter(Alert.id.in_(alert_ids))
            .all()
        )
        incident.alerts = alerts
    return incident


def update_incident(
    db: Session,
    incident: Incident,
    title: Optional[str] = None,
    description: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    resolution: Optional[str] = None,
) -> Incident:
    if title is not None:
        incident.title = title
    if description is not None:
        incident.description = description
    if severity is not None:
        incident.severity = severity
    if assigned_to is not None:
        incident.assigned_to = assigned_to
    if resolution is not None:
        incident.resolution = resolution
    if status is not None:
        allowed = VALID_TRANSITIONS.get(incident.status, [])
        if status != incident.status and status not in allowed:
            raise ValueError(
                "Invalid incident status transition from "
                + incident.status + " to " + status
            )
        incident.status = status
        if status == "closure":
            incident.closed_at = datetime.now(timezone.utc)
    db.add(incident)
    db.flush()
    return incident


def associate_alerts(db: Session, incident: Incident, alert_ids: List[int]) -> Incident:
    alerts = (
        db.query(Alert)
        .filter(Alert.id.in_(alert_ids))
        .all()
    )
    for alert in alerts:
        if alert not in incident.alerts:
            incident.alerts.append(alert)
    db.add(incident)
    db.flush()
    return incident


def add_note(
    db: Session,
    incident: Incident,
    user_id: int,
    note: str,
) -> IncidentNote:
    entry = IncidentNote(
        incident_id=incident.id,
        user_id=user_id,
        note=note,
    )
    db.add(entry)
    db.flush()
    return entry


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
