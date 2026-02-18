"""
Async and sync SQLAlchemy engine helpers.
- Async engine (aiomysql) used by the running FastAPI app
- Sync engine (pymysql) used ONLY for offline model generation scripts
Usage:
- Use `Depends(get_session)` in FastAPI routes/services to obtain AsyncSession
"""

from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Async Engine for runtime
async_engine: AsyncEngine = create_async_engine(
    settings.effective_database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Correct: Use async_sessionmaker instead of sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        # Context manager automatically closes the session


def get_sync_engine():
    """
    Return a synchronous engine for model-reflection scripts (e.g. Alembic, model generation).
    Converts mysql+aiomysql://... → mysql+pymysql://...
    """
    sync_url = str(settings.effective_database_url)
    if "+aiomysql" in sync_url:
        sync_url = sync_url.replace("+aiomysql", "+pymysql")
    return create_engine(sync_url, future=True, echo=False)