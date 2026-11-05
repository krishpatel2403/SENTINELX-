"""Detection rule schemas."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class DetectionRuleBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: str
    mitre_technique_id: Optional[str] = Field(default=None, max_length=50)
    mitre_tactic: Optional[str] = Field(default=None, max_length=100)
    severity: str = Field(default="medium", max_length=50)
    threshold: int = Field(default=5, ge=1)
    time_window: int = Field(default=300, ge=1)  # seconds
    enabled: bool = True
    rule_type: str = Field(..., max_length=100)
    config: Dict[str, Any] = {}


class DetectionRuleCreate(DetectionRuleBase):
    pass


class DetectionRuleUpdate(BaseModel):
    description: Optional[str] = None
    mitre_technique_id: Optional[str] = None
    mitre_tactic: Optional[str] = None
    severity: Optional[str] = None
    threshold: Optional[int] = Field(default=None, ge=1)
    time_window: Optional[int] = Field(default=None, ge=1)
    enabled: Optional[bool] = None
    rule_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


from datetime import datetime


class DetectionRuleOut(DetectionRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
