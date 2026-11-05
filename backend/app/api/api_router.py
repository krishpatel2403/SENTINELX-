"""Versioned API router assembly.

Each module registers its routes under a dedicated prefix. Routers are added
here as modules are implemented across milestones.
"""

from fastapi import APIRouter

api_router = APIRouter()

# Placeholder routers — included as they are implemented.
from app.api import auth, users, events, ingestion, rules, alerts, incidents, intelligence, mitre, reports, dashboard

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(rules.router, prefix="/rules", tags=["detection-rules"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(mitre.router, prefix="/mitre", tags=["mitre"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
