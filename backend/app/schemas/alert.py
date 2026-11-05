"""Alert schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AlertBase(BaseModel):
    rule_id: int
    event_id: int
    title: str = Field(..., max_length=255)
    description: str
    severity: str = Field(..., max_length=50)
    status: str = Field(default="new", max_length=50)  # new | investigating | escalated | resolved | false_positive
    assigned_to: Optional[int] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    severity: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=50)
    assigned_to: Optional[int] = None


class AlertOut(AlertBase):
    id: int
    alert_id: str
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertFilter(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    assigned_to: Optional[int] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class AlertList(BaseModel):
    items: List[AlertOut]
    total: int
    page: int
    page_size: int
