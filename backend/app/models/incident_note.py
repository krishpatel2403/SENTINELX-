"""IncidentNote model — analyst investigation notes attached to incidents."""

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAt, UpdatedAt


class IncidentNote(Base):
    __tablename__ = "incident_notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    note: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="notes")
    author: Mapped["User"] = relationship("User", back_populates="incident_notes")
