"""
Database Session Management
===========================
SQLAlchemy async engine and sessionmaker configuration.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Create async engine for PostgreSQL
engine = create_async_engine(
    str(settings.POSTGRES_ASYNC_URI),
    echo=settings.DEBUG,
    future=True,
    pool_size=20,
    max_overflow=10,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields a database session.
    Automatically closes the session after the request finishes.
    """
    async with AsyncSessionLocal() as session:
        yield session
