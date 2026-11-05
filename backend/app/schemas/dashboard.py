"""Dashboard schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    total_events: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    active_incidents: int
    resolved_incidents: int
    auth_failures: int
    suspicious_ips: int


class ChartSeries(BaseModel):
    name: str
    data: List[Any]


class DashboardChart(BaseModel):
    title: str
    series: List[ChartSeries]
