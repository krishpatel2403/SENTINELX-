"""Incident schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.alert import AlertOut


class IncidentBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    severity: str = Field(..., max_length=50)
    status: str = Field(default="detection", max_length=50)  # detection | triage | investigation | containment | recovery | closure
    assigned_to: Optional[int] = None
    resolution: Optional[str] = None
    alert_ids: Optional[List[int]] = None


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    severity: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=50)
    assigned_to: Optional[int] = None
    resolution: Optional[str] = None


class IncidentOut(IncidentBase):
    id: int
    incident_id: str
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    alerts: List[AlertOut] = []

    model_config = {"from_attributes": True}


class IncidentFilter(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    assigned_to: Optional[int] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class IncidentList(BaseModel):
    items: List[IncidentOut]
    total: int
    page: int
    page_size: int
