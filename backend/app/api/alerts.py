'''Alert management API.'''

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_analyst
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import (
    AlertCreate,
    AlertList,
    AlertOut,
    AlertUpdate,
)
from app.services import alerts as alert_service

router = APIRouter()


@router.get("/", response_model=AlertList, tags=["alerts"])
def list_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    items, total = alert_service.list_alerts(
        db, status=status, severity=severity, assigned_to=assigned_to,
        search=search, page=page, page_size=page_size,
    )
    return AlertList(items=items, total=total, page=page, page_size=page_size)


@router.get("/{alert_id}", response_model=AlertOut, tags=["alerts"])
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/", response_model=AlertOut, status_code=201, tags=["alerts"])
def create_alert(
    alert_in: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    alert = alert_service.create_alert(
        db,
        rule_id=alert_in.rule_id,
        event_id=alert_in.event_id,
        title=alert_in.title,
        description=alert_in.description,
        severity=alert_in.severity,
        status=alert_in.status,
        assigned_to=alert_in.assigned_to,
    )
    db.commit()
    alert_service.audit(
        db, current_user.id, "create_alert", "alert", str(alert.id),
        {"title": alert.title, "severity": alert.severity},
    )
    db.commit()
    return alert


@router.patch("/{alert_id}", response_model=AlertOut, tags=["alerts"])
def update_alert(
    alert_id: int,
    alert_in: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert = alert_service.update_alert(
        db, alert,
        title=alert_in.title,
        description=alert_in.description,
        severity=alert_in.severity,
        status=alert_in.status,
        assigned_to=alert_in.assigned_to,
    )
    db.commit()
    alert_service.audit(
        db, current_user.id, "update_alert", "alert", str(alert.id),
        {"status": alert.status, "assigned_to": alert.assigned_to},
    )
    db.commit()
    return alert
