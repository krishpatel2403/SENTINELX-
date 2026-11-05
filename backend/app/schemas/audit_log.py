"""Audit log schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogList(BaseModel):
    items: List[AuditLogOut]
    total: int
    page: int
    page_size: int
