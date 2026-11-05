"""ThreatIndicator model — IOC enrichment records."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAt, UpdatedAt


class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    indicator_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # ip | domain | hash | url
    indicator_value: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    classification: Mapped[str] = mapped_column(String(50), default="unknown", nullable=False)  # malicious | suspicious | benign | unknown
    reputation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # feed or "local"
    confidence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-100
    first_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_threat_indicators_type_classification", "indicator_type", "classification"),
    )
