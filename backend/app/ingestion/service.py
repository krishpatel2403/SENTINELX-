'''Ingestion service: parse uploaded log files, normalize, deduplicate, report.

Nothing is silently discarded: every record is accepted, rejected (malformed),
or skipped (duplicate), and an ingestion report is produced.
'''

from __future__ import annotations

import hashlib
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.ingestion.parser import (
    iter_csv_rows,
    iter_json_lines,
    parse_csv_record,
    parse_json_record,
    parse_syslog_line,
    parse_windows_event,
    _make_event_id,
    _normalize_dict,
)
from app.models.security_event import SecurityEvent
from app.schemas.ingestion import IngestionReport, IngestionRecordResult


class IngestionService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #
    def ingest_upload(
        self,
        filename: str,
        content_bytes: bytes,
        source: Optional[str] = None,
    ) -> IngestionReport:
        """Ingest an uploaded log file and return an ingestion report."""
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = content_bytes.decode("utf-8", errors="replace")

        detected_source = source or self._detect_source(filename, content)
        records = self._split_records(content, detected_source)

        results: List[IngestionRecordResult] = []
        accepted = rejected = skipped = duplicates = 0

        for index, raw_record in enumerate(records, start=1):
            line_number = index
            event_dict, reject_reason = self._parse_record(raw_record, detected_source)

            if reject_reason:
                rejected += 1
                results.append(IngestionRecordResult(
                    line_number=line_number, accepted=False,
                    event_id=None, reason=reject_reason))
                continue

            # Validate required fields.
            if not event_dict.get("event_id") or not event_dict.get("timestamp"):
                rejected += 1
                results.append(IngestionRecordResult(
                    line_number=line_number, accepted=False,
                    event_id=None, reason="missing required field(s) (event_id/timestamp)"))
                continue

            event_id = event_dict["event_id"]

            # Deduplication against the database.
            existing = self.db.query(SecurityEvent).filter(
                SecurityEvent.event_id == event_id).first()
            if existing:
                skipped += 1
                duplicates += 1
                results.append(IngestionRecordResult(
                    line_number=line_number, accepted=False,
                    event_id=event_id, reason="duplicate event_id"))
                continue

            # Persist the normalized event.
            db_event = SecurityEvent(
                event_id=event_id,
                timestamp=event_dict["timestamp"],
                source=event_dict.get("source") or detected_source,
                hostname=event_dict.get("hostname"),
                username=event_dict.get("username"),
                source_ip=event_dict.get("source_ip"),
                destination_ip=event_dict.get("destination_ip"),
                event_type=event_dict.get("event_type") or "unknown",
                severity=str(event_dict.get("severity") or "low").lower(),
                description=event_dict.get("description") or "",
                raw_event=event_dict.get("raw_event") or {},
                event_metadata=event_dict.get("event_metadata") or {},
                is_duplicate=False,
                original_event_id=None,
            )
            self.db.add(db_event)
            accepted += 1
            results.append(IngestionRecordResult(
                line_number=line_number, accepted=True,
                event_id=event_id, reason=None))

        self.db.commit()

        total = len(records)
        return IngestionReport(
            filename=filename,
            total_records=total,
            accepted=accepted,
            rejected=rejected,
            skipped=skipped,
            duplicates=duplicates,
            results=results,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _detect_source(self, filename: str, content: str) -> str:
        name = filename.lower()
        stripped = content.strip()
        if name.endswith(".json") or stripped.startswith(("{", "[")):
            return "json"
        if name.endswith(".csv"):
            return "csv"
        if name.endswith(".evtx") or "windows" in name:
            return "windows_event"
        return "linux_auth"

    def _split_records(self, content: str, source: str) -> List[Any]:
        if source == "csv":
            return iter_csv_rows(content)
        if source == "json":
            # JSON array or JSON lines.
            stripped = content.strip()
            if stripped.startswith("["):
                try:
                    import json as _json
                    data = _json.loads(stripped)
                    if isinstance(data, list):
                        return data
                except Exception:
                    pass
            return iter_json_lines(content)
        # Default: treat each non-empty line as a syslog/auth record.
        return [line for line in content.splitlines() if line.strip()]

    def _parse_record(self, raw_record: Any, source: str) -> Tuple[Dict[str, Any], Optional[str]]:
        if source == "csv" and isinstance(raw_record, dict):
            return parse_csv_record(raw_record, source)
        if source == "json":
            if isinstance(raw_record, dict):
                # Already a dict (from JSON array): normalize directly.
                return _normalize_dict(raw_record, source), None
            return parse_json_record(str(raw_record), source)
        if source == "windows_event":
            if isinstance(raw_record, dict):
                return parse_windows_event(raw_record, source)
            return parse_json_record(str(raw_record), source)
        # Default syslog/auth line parsing.
        if isinstance(raw_record, dict):
            return _normalize_dict(raw_record, source), None
        return parse_syslog_line(str(raw_record), source)
