"""User model — authentication and RBAC."""

from typing import List, Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAt, UpdatedAt


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="analyst", nullable=False)  # admin | analyst
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps inherited from Base: created_at, updated_at

    # Relationships
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )
    incident_notes: Mapped[List["IncidentNote"]] = relationship(
        "IncidentNote", back_populates="author", cascade="all, delete-orphan"
    )
    assigned_incidents: Mapped[List["Incident"]] = relationship(
        "Incident", foreign_keys="Incident.assigned_to", back_populates="assignee"
    )
    assigned_alerts: Mapped[List["Alert"]] = relationship(
        "Alert", foreign_keys="Alert.assigned_to", back_populates="assignee"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
