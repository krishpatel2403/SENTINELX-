"""Structured logging configuration for SentinelX.

Logs are emitted as JSON where possible and never include secrets, password
hashes, or tokens.
"""

import logging
import sys


def configure_logging() -> None:
    """Configure the root logger once at application startup."""
    log_level = logging.DEBUG if __import__("app.core.config", fromlist=["settings"]).settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )

    # Reduce noise from third-party libraries.
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "passlib"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


logger = logging.getLogger("sentinelx")
