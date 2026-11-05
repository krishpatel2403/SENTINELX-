"""Log ingestion schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IngestionRecordResult(BaseModel):
    line_number: int
    accepted: bool
    event_id: Optional[str] = None
    reason: Optional[str] = None


class IngestionReport(BaseModel):
    filename: str
    total_records: int
    accepted: int
    rejected: int
    skipped: int
    duplicates: int
    results: List[IngestionRecordResult] = []

    model_config = {"from_attributes": True}


class IngestionResponse(BaseModel):
    report: IngestionReport
    message: str
