"""Database session management."""

from typing import AsyncGenerator

import asyncio
import logging
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


# Create async engine
engine = create_async_engine(
    # Ensure the database URL uses the correct format: postgresql+asyncpg://
    # If it's already in the correct format in settings, this won't change anything
    settings.DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://').replace('postgresql://', 'postgresql+asyncpg://'),
    echo=settings.DB_ECHO,
    future=True,
    connect_args={"ssl": "require"},  # Pass SSL requirement here
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    logger.debug("Creating database session.")
    async with async_session_factory() as session:
        try:
            logger.debug("Yielding database session.")
            yield session
            logger.debug("Committing database session.")
            await session.commit()
            logger.debug("Database session committed.")
        except Exception as e:
            logger.error(f"Error during database session: {e}")
            await session.rollback()
            raise
        finally:
            logger.debug("Closing database session.")