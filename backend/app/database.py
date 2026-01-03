"""
Database configuration and session management.
Uses SQLAlchemy with SQLite for offline data persistence.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.config import settings

logger = logging.getLogger(__name__)

# Ensure data directory exists
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.AI_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Create synchronous engine for initialization
sync_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.DEBUG
)

# Create async engine for runtime
async_engine = create_async_engine(
    settings.DATABASE_ASYNC_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


# Enable foreign keys for SQLite
@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key support in SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """Get a synchronous database session."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Initialize database tables."""
    from app.models import db_models  # Import to register models
    Base.metadata.create_all(bind=sync_engine)
    logger.info("Database initialized successfully")


async def close_db():
    """Close database connections."""
    await async_engine.dispose()
    sync_engine.dispose()
    logger.info("Database connections closed")
