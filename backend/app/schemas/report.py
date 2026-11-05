"""Report schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ReportGenerate(BaseModel):
    format: str = Field(default="json", pattern="^(pdf|json|csv)$")
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class ReportRecordOut(BaseModel):
    id: int
    report_id: str
    format: str
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    generated_by: Optional[int]
    file_path: Optional[str]
    checksum: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
