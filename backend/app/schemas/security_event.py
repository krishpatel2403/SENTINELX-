"""Security event schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SecurityEventBase(BaseModel):
    event_id: str = Field(..., max_length=255)
    timestamp: datetime
    source: str = Field(..., max_length=100)
    hostname: Optional[str] = Field(default=None, max_length=255)
    username: Optional[str] = Field(default=None, max_length=255)
    source_ip: Optional[str] = Field(default=None, max_length=64)
    destination_ip: Optional[str] = Field(default=None, max_length=64)
    event_type: str = Field(..., max_length=100)
    severity: str = Field(..., max_length=50)  # low | medium | high | critical
    description: str
    raw_event: Dict[str, Any]
    event_metadata: Dict[str, Any] = {}


class SecurityEventCreate(SecurityEventBase):
    pass


class SecurityEventOut(SecurityEventBase):
    id: int
    is_duplicate: bool
    original_event_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SecurityEventFilter(BaseModel):
    source: Optional[str] = None
    severity: Optional[str] = None
    event_type: Optional[str] = None
    username: Optional[str] = None
    source_ip: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class SecurityEventList(BaseModel):
    items: List[SecurityEventOut]
    total: int
    page: int
    page_size: int
