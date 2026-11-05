"""Association (many-to-many) tables."""

from sqlalchemy import Column, ForeignKey, Integer, Table

from app.models.base import Base

incident_alerts = Table(
    "incident_alerts",
    Base.metadata,
    Column("incident_id", ForeignKey("incidents.id"), primary_key=True, nullable=False),
    Column("alert_id", ForeignKey("alerts.id"), primary_key=True, nullable=False),
)
