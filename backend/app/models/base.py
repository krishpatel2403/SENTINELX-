"""Base model with common timestamp columns."""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Backwards-compatible type aliases imported by several model modules.
# The actual mapped columns are defined on `Base` below.
CreatedAt = datetime
UpdatedAt = datetime


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all SentinelX models.

    Every model inherits `created_at` and `updated_at` timestamp columns.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
