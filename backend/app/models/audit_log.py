"""AuditLog model — append-only record of authenticated actions."""

from typing import Any, Dict, Optional

from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAt, UpdatedAt


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. login, create_alert, import_logs
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. alert, incident, user
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)  # redacted of secrets
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
