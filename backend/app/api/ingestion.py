"""Log ingestion API — upload, parse, normalize, deduplicate, report."""

from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_analyst
from app.core.config import settings
from app.ingestion.service import IngestionService
from app.models.user import User
from app.schemas.ingestion import IngestionReport

router = APIRouter()


def _validate_upload(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    if settings.MAX_UPLOAD_SIZE_MB and file.size and file.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File exceeds " + str(settings.MAX_UPLOAD_SIZE_MB) + " MB limit",
        )


@router.post("/upload", response_model=IngestionReport, tags=["ingestion"])
async def upload_logs(
    file: UploadFile = File(...),
    source: Optional[str] = Query(None, description="Override auto-detected source type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Upload a log file for ingestion.

    Supported: Linux auth/syslog, system logs, Windows event exports,
    JSON security events (JSON lines or array), CSV security events.

    Returns an ingestion report with accepted / rejected / skipped counts.
    Malformed records are rejected with a reason, never silently discarded.
    """
    _validate_upload(file)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    service = IngestionService(db)
    try:
        report = service.ingest_upload(file.filename or "upload", content, source)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Ingestion failed: " + str(exc))
    return report


@router.get("/sources", tags=["ingestion"])
def supported_sources():
    """List supported log source types."""
    return {
        "sources": [
            {"id": "linux_auth", "label": "Linux authentication logs"},
            {"id": "syslog", "label": "Linux system logs (syslog)"},
            {"id": "windows_event", "label": "Windows event log export"},
            {"id": "json", "label": "JSON security events"},
            {"id": "csv", "label": "CSV security events"},
        ]
    }
