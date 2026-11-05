'''Threat intelligence API.'''

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_analyst
from app.intelligence.service import IntelligenceService
from app.models.threat_indicator import ThreatIndicator
from app.models.user import User
from app.schemas.threat_indicator import (
    ThreatIndicatorCreate,
    ThreatIndicatorFilter,
    ThreatIndicatorList,
    ThreatIndicatorOut,
)

router = APIRouter()


@router.get("/indicators", response_model=ThreatIndicatorList, tags=["intelligence"])
def list_indicators(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
    indicator_type: Optional[str] = Query(None),
    classification: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    service = IntelligenceService(db)
    items, total = service.list_indicators(
        indicator_type=indicator_type,
        classification=classification,
        search=search,
        page=page,
        page_size=page_size,
    )
    return ThreatIndicatorList(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/enrich/{indicator_type}/{indicator_value:path}",
    tags=["intelligence"],
)
def enrich_indicator(
    indicator_type: str = Path(..., description="ip | domain | hash | url"),
    indicator_value: str = Path(..., description="The IOC value to enrich"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    service = IntelligenceService(db)
    return service.enrich(indicator_type, indicator_value)


@router.post("/indicators", response_model=ThreatIndicatorOut, status_code=201, tags=["intelligence"])
def upsert_indicator(
    indicator_in: ThreatIndicatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    service = IntelligenceService(db)
    indicator = service.upsert_indicator(
        indicator_type=indicator_in.indicator_type,
        indicator_value=indicator_in.indicator_value,
        classification=indicator_in.classification,
        reputation=indicator_in.reputation,
        source=indicator_in.source or "local",
        confidence=indicator_in.confidence,
    )
    db.commit()
    return indicator
