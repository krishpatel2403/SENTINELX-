"""SecurityEvent model — normalized common security event schema.

The original raw event is preserved in `raw_event` and `event_metadata` for
investigation. Nothing is silently discarded.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, String, Text, Boolean, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAt, UpdatedAt


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # External, immutable event identifier from the source system.
    event_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. linux_auth, syslog, windows_event, json, csv
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    destination_ip: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # low | medium | high | critical
    description: Mapped[str] = mapped_column(Text, nullable=False)
    raw_event: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)  # original event payload
    event_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    original_event_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_security_events_timestamp_source", "timestamp", "source"),
        Index("ix_security_events_source_ip", "source_ip"),
        Index("ix_security_events_username", "username"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SecurityEvent(id={self.id}, event_id={self.event_id}, severity={self.severity})>"
