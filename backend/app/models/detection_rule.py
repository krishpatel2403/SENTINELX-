"""DetectionRule model — configurable detection rules."""

from typing import Any, Dict, List, Optional

from sqlalchemy import String, Text, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAt, UpdatedAt


class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    mitre_technique_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g. T1110
    mitre_tactic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g. Credential Access
    severity: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)  # low | medium | high | critical
    threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # event count threshold
    time_window: Mapped[int] = mapped_column(Integer, default=300, nullable=False)  # seconds
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rule_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. brute_force, ioc_match, frequency
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)  # extra rule-specific config

    # Relationships
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DetectionRule(id={self.id}, name={self.name}, enabled={self.enabled})>"
