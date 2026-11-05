'''Threat intelligence service.

Provides IOC enrichment for IP addresses, domains, file hashes and URLs.
Distinguishes "no intelligence available" (unknown) from a clean/benign result.
Optional public threat-intel feeds are only used when configured.
'''

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.threat_indicator import ThreatIndicator


class IntelligenceService:
    def __init__(self, db: Session):
        self.db = db

    def enrich(
        self,
        indicator_type: str,
        indicator_value: str,
    ) -> Dict[str, Any]:
        """Enrich a single IOC.

        Returns a dict with classification, reputation, source, confidence,
        first_seen, last_seen and an `available` flag.

        `available=False` means no intelligence exists for the IOC -- this is
        explicitly distinct from a clean/benign result.
        """
        indicator_type = indicator_type.lower().strip()
        value = indicator_value.strip()

        local = (
            self.db.query(ThreatIndicator)
            .filter(ThreatIndicator.indicator_type == indicator_type)
            .filter(ThreatIndicator.indicator_value == value)
            .first()
        )

        if local:
            return {
                "indicator_type": indicator_type,
                "indicator_value": value,
                "classification": local.classification,
                "reputation": local.reputation,
                "source": local.source or "local",
                "confidence": local.confidence,
                "first_seen": local.first_seen.isoformat() if local.first_seen else None,
                "last_seen": local.last_seen.isoformat() if local.last_seen else None,
                "available": True,
            }

        # Optional public feed lookup (only when configured).
        if settings.THREAT_FEED_ENABLED and settings.THREAT_FEED_URL:
            feed_result = self._query_public_feed(indicator_type, value)
            if feed_result:
                return feed_result

        # No intelligence available -- explicitly NOT a clean result.
        return {
            "indicator_type": indicator_type,
            "indicator_value": value,
            "classification": "unknown",
            "reputation": None,
            "source": "none",
            "confidence": None,
            "first_seen": None,
            "last_seen": None,
            "available": False,
        }

    def upsert_indicator(
        self,
        indicator_type: str,
        indicator_value: str,
        classification: str = "unknown",
        reputation: Optional[str] = None,
        source: Optional[str] = "local",
        confidence: Optional[int] = None,
    ) -> ThreatIndicator:
        indicator_type = indicator_type.lower().strip()
        value = indicator_value.strip()
        now = datetime.now(timezone.utc)

        existing = (
            self.db.query(ThreatIndicator)
            .filter(ThreatIndicator.indicator_type == indicator_type)
            .filter(ThreatIndicator.indicator_value == value)
            .first()
        )
        if existing:
            existing.classification = classification
            existing.reputation = reputation
            existing.source = source
            existing.confidence = confidence
            existing.last_seen = now
            if not existing.first_seen:
                existing.first_seen = now
            self.db.add(existing)
            self.db.flush()
            return existing

        indicator = ThreatIndicator(
            indicator_type=indicator_type,
            indicator_value=value,
            classification=classification,
            reputation=reputation,
            source=source,
            confidence=confidence,
            first_seen=now,
            last_seen=now,
        )
        self.db.add(indicator)
        self.db.flush()
        return indicator

    def list_indicators(
        self,
        indicator_type: Optional[str] = None,
        classification: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        query = self.db.query(ThreatIndicator)
        if indicator_type:
            query = query.filter(ThreatIndicator.indicator_type == indicator_type)
        if classification:
            query = query.filter(ThreatIndicator.classification == classification)
        if search:
            like = "%" + search + "%"
            query = query.filter(ThreatIndicator.indicator_value.like(like))
        total = query.count()
        items = (
            query.order_by(ThreatIndicator.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    # ------------------------------------------------------------------ #
    # Internal
    # ------------------------------------------------------------------ #
    def _query_public_feed(self, indicator_type: str, value: str) -> Optional[Dict[str, Any]]:
        """Placeholder for optional public threat-intel feed integration.

        Not implemented by default so the platform works offline. When
        THREAT_FEED_ENABLED is set, this is where a feed client would be wired
        in. Returns None when no feed data is available.
        """
        # Intentionally offline by default.
        return None
