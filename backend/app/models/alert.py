"""Alert model — detection results assigned to analysts."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import incident_alerts
from app.models.base import Base, CreatedAt, UpdatedAt


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    alert_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    rule_id: Mapped[int] = mapped_column(ForeignKey("detection_rules.id"), nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("security_events.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False, index=True)  # new | investigating | escalated | resolved | false_positive
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    rule: Mapped["DetectionRule"] = relationship("DetectionRule", back_populates="alerts")
    event: Mapped["SecurityEvent"] = relationship("SecurityEvent", back_populates="alerts")
    assignee: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assigned_to], back_populates="assigned_alerts"
    )
    incidents: Mapped[List["Incident"]] = relationship(
        "Incident", secondary=incident_alerts, back_populates="alerts"
    )

    __table_args__ = (
        Index("ix_alerts_status_severity", "status", "severity"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Alert(id={self.id}, alert_id={self.alert_id}, status={self.status})>"
