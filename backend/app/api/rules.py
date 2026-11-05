'''Detection rules API — CRUD and on-demand evaluation.'''

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_analyst, require_admin
from app.core.security import get_password_hash
from app.detection.engine import DetectionEngine
from app.models.detection_rule import DetectionRule
from app.models.user import User
from app.schemas.detection_rule import (
    DetectionRuleCreate,
    DetectionRuleOut,
    DetectionRuleUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[DetectionRuleOut], tags=["detection-rules"])
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
    enabled: Optional[bool] = None,
):
    query = db.query(DetectionRule)
    if enabled is not None:
        query = query.filter(DetectionRule.enabled == enabled)
    return query.all()


@router.get("/{rule_id}", response_model=DetectionRuleOut, tags=["detection-rules"])
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.post("/", response_model=DetectionRuleOut, status_code=201, tags=["detection-rules"])
def create_rule(
    rule_in: DetectionRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.query(DetectionRule).filter(DetectionRule.name == rule_in.name).first():
        raise HTTPException(status_code=400, detail="Rule already exists")
    rule = DetectionRule(**rule_in.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.patch("/{rule_id}", response_model=DetectionRuleOut, tags=["detection-rules"])
def update_rule(
    rule_id: int,
    rule_in: DetectionRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in rule_in.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204, tags=["detection-rules"])
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return None


@router.post("/evaluate", tags=["detection-rules"])
def evaluate_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Run the detection engine against current events and create alerts."""
    engine = DetectionEngine(db)
    created = engine.evaluate_all()
    db.commit()
    return {
        "created_alerts": len(created),
        "alerts": [
            {
                "id": a.id,
                "alert_id": a.alert_id,
                "rule_id": a.rule_id,
                "title": a.title,
                "severity": a.severity,
                "status": a.status,
            }
            for a in created
        ],
    }
