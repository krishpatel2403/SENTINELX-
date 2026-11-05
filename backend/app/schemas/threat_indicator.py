"""Threat indicator schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ThreatIndicatorBase(BaseModel):
    indicator_type: str = Field(..., max_length=50)  # ip | domain | hash | url
    indicator_value: str = Field(..., max_length=512)
    classification: str = Field(default="unknown", max_length=50)  # malicious | suspicious | benign | unknown
    reputation: Optional[str] = Field(default=None, max_length=100)
    source: Optional[str] = Field(default=None, max_length=100)
    confidence: Optional[int] = Field(default=None, ge=0, le=100)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class ThreatIndicatorCreate(ThreatIndicatorBase):
    pass


class ThreatIndicatorOut(ThreatIndicatorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ThreatIndicatorFilter(BaseModel):
    indicator_type: Optional[str] = None
    classification: Optional[str] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class ThreatIndicatorList(BaseModel):
    items: List[ThreatIndicatorOut]
    total: int
    page: int
    page_size: int
