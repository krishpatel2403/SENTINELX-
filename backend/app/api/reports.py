"""Report generation API — stub (Milestone 7/J)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_analyst
from app.models.user import User

router = APIRouter()


@router.post("/generate", tags=["reports"])
def generate_report(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    raise HTTPException(status_code=501, detail="Report generation service in Milestone 7")


@router.get("/", tags=["reports"])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    raise HTTPException(status_code=501, detail="Report generation service in Milestone 7")
