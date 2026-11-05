"""Security dashboard API — real statistics from application data."""

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user, require_analyst
from app.models.security_event import SecurityEvent
from app.models.user import User

router = APIRouter()


@router.get("/stats", tags=["dashboard"])
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    total_events = db.query(SecurityEvent).count()
    by_severity = {}
    for sev in ("critical", "high", "medium", "low"):
        by_severity[sev] = (
            db.query(SecurityEvent).filter(SecurityEvent.severity == sev).count()
        )
    return {
        "total_events": total_events,
        "by_severity": by_severity,
        "critical_alerts": by_severity.get("critical", 0),
        "high_alerts": by_severity.get("high", 0),
        "medium_alerts": by_severity.get("medium", 0),
        "low_alerts": by_severity.get("low", 0),
    }


@router.get("/events-over-time", tags=["dashboard"])
def events_over_time(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
    days: int = Query(7, ge=1, le=30),
):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            func.date(SecurityEvent.timestamp).label("date"),
            func.count(SecurityEvent.id).label("count"),
        )
        .filter(SecurityEvent.timestamp >= since)
        .group_by(func.date(SecurityEvent.timestamp))
        .all()
    )
    return [{"date": str(r.date), "count": r.count} for r in rows]
