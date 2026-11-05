"""Security events API — list, filter, and retrieve normalized events."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_analyst
from app.models.security_event import SecurityEvent
from app.models.user import User
from app.schemas.security_event import (
    SecurityEventOut,
    SecurityEventFilter,
    SecurityEventList,
)

router = APIRouter()


def _apply_filters(query, f: SecurityEventFilter):
    if f.source:
        query = query.filter(SecurityEvent.source == f.source)
    if f.severity:
        query = query.filter(SecurityEvent.severity == f.severity)
    if f.event_type:
        query = query.filter(SecurityEvent.event_type == f.event_type)
    if f.username:
        query = query.filter(SecurityEvent.username.ilike(f"%{f.username}%"))
    if f.source_ip:
        query = query.filter(SecurityEvent.source_ip == f.source_ip)
    if f.start_time:
        query = query.filter(SecurityEvent.timestamp >= f.start_time)
    if f.end_time:
        query = query.filter(SecurityEvent.timestamp <= f.end_time)
    if f.search:
        like = f"%{f.search}%"
        query = query.filter(
            (SecurityEvent.hostname.ilike(like))
            | (SecurityEvent.description.ilike(like))
            | (SecurityEvent.source_ip.ilike(like))
        )
    return query


@router.get("/", response_model=SecurityEventList, tags=["events"])
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
    source: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    source_ip: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    filter_in = SecurityEventFilter(
        source=source,
        severity=severity,
        event_type=event_type,
        username=username,
        source_ip=source_ip,
        start_time=start_time,
        end_time=end_time,
        search=search,
        page=page,
        page_size=page_size,
    )
    query = db.query(SecurityEvent)
    query = _apply_filters(query, filter_in)
    total = query.count()
    items = (
        query.order_by(SecurityEvent.timestamp.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return SecurityEventList(items=items, total=total, page=page, page_size=page_size)


@router.get("/{event_id}", response_model=SecurityEventOut, tags=["events"])
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/stats/summary", tags=["events"])
def events_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    total = db.query(SecurityEvent).count()
    by_severity = {}
    for sev in ("critical", "high", "medium", "low"):
        by_severity[sev] = (
            db.query(SecurityEvent).filter(SecurityEvent.severity == sev).count()
        )
    return {"total_events": total, "by_severity": by_severity}
