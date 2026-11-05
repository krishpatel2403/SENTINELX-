"""ReportRecord model — generated security reports."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAt, UpdatedAt


class ReportRecord(Base):
    __tablename__ = "report_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf | json | csv
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    generated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # SHA-256

    generated_by_user: Mapped[Optional["User"]] = relationship("User")
