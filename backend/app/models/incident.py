"""Incident model — security incident lifecycle management."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import incident_alerts
from app.models.base import Base, CreatedAt, UpdatedAt


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(50), default="detection", nullable=False, index=True
    )  # detection | triage | investigation | containment | recovery | closure
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    assignee: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assigned_to], back_populates="assigned_incidents"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", secondary=incident_alerts, back_populates="incidents"
    )
    notes: Mapped[List["IncidentNote"]] = relationship(
        "IncidentNote", back_populates="incident", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_incidents_status_severity", "status", "severity"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Incident(id={self.id}, incident_id={self.incident_id}, status={self.status})>"
