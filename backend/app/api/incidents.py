'''Incident management API.'''

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_analyst
from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentFilter,
    IncidentList,
    IncidentOut,
    IncidentUpdate,
)
from app.schemas.incident_note import IncidentNoteCreate, IncidentNoteOut
from app.services import incidents as incident_service

router = APIRouter()


@router.get("/", response_model=IncidentList, tags=["incidents"])
def list_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    items, total = incident_service.list_incidents(
        db, status=status, severity=severity, assigned_to=assigned_to,
        search=search, page=page, page_size=page_size,
    )
    return IncidentList(items=items, total=total, page=page, page_size=page_size)


@router.get("/{incident_id}", response_model=IncidentOut, tags=["incidents"])
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/", response_model=IncidentOut, status_code=201, tags=["incidents"])
def create_incident(
    incident_in: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    incident = incident_service.create_incident(
        db,
        title=incident_in.title,
        description=incident_in.description,
        severity=incident_in.severity,
        status=incident_in.status,
        assigned_to=incident_in.assigned_to,
        alert_ids=incident_in.alert_ids if hasattr(incident_in, "alert_ids") else None,
    )
    db.commit()
    incident_service.audit(
        db, current_user.id, "create_incident", "incident", str(incident.id),
        {"title": incident.title, "severity": incident.severity},
    )
    db.commit()
    return incident


@router.patch("/{incident_id}", response_model=IncidentOut, tags=["incidents"])
def update_incident(
    incident_id: int,
    incident_in: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    try:
        incident = incident_service.update_incident(
            db, incident,
            title=incident_in.title,
            description=incident_in.description,
            severity=incident_in.severity,
            status=incident_in.status,
            assigned_to=incident_in.assigned_to,
            resolution=incident_in.resolution,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    db.commit()
    incident_service.audit(
        db, current_user.id, "update_incident", "incident", str(incident.id),
        {"status": incident.status},
    )
    db.commit()
    return incident


@router.post("/{incident_id}/notes", response_model=IncidentNoteOut, status_code=201, tags=["incidents"])
def add_incident_note(
    incident_id: int,
    note_in: IncidentNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    note = incident_service.add_note(db, incident, current_user.id, note_in.note)
    db.commit()
    return note
