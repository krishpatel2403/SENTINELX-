"""Incident note schemas."""

from datetime import datetime
from pydantic import BaseModel


class IncidentNoteBase(BaseModel):
    note: str


class IncidentNoteCreate(IncidentNoteBase):
    pass


class IncidentNoteOut(IncidentNoteBase):
    id: int
    incident_id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
