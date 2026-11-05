"""SQLAlchemy database engine, session, and base model.

SQLite is the default database. Set `DATABASE_URL` to a PostgreSQL connection
string for production deployments.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import Base

_connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # `check_same_thread=False` is required for SQLite with FastAPI's thread pool.
    _connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
