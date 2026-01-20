"""Database configuration and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import Optional
from app.core.config import settings

# Base class for models (safe - no side effects)
Base = declarative_base()

# Lazy-initialized globals
_engine: Optional[object] = None
_AsyncSessionLocal: Optional[object] = None


def get_engine():
    """Get or create the async engine (lazy initialization).
    
    This prevents issues with tests that use synchronous SQLite by deferring
    engine creation until it's actually needed in production.
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            future=True,
        )
    return _engine


def get_async_session_factory():
    """Get or create the async session factory (lazy initialization).
    
    Returns the async session maker for creating database sessions.
    """
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        engine = get_engine()
        _AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


# Legacy support: Expose as module-level attributes
def _get_async_session_local():
    """Backward compatibility getter for AsyncSessionLocal."""
    return get_async_session_factory()


# Create a property-like object for backward compatibility
class _AsyncSessionLocalProxy:
    """Proxy to maintain backward compatibility with AsyncSessionLocal."""
    def __call__(self, *args, **kwargs):
        return get_async_session_factory()(*args, **kwargs)
    
    def __enter__(self):
        return get_async_session_factory().__enter__()
    
    def __aenter__(self):
        return get_async_session_factory().__aenter__()


# Backward compatible reference
AsyncSessionLocal = _AsyncSessionLocalProxy()


async def get_db() -> AsyncSession:
    """Dependency to get database session.
    
    This is a FastAPI dependency that provides a database session for each request.
    """
    SessionLocal = get_async_session_factory()
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


