"""Configuration for integration tests - shared async database per test."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base


@pytest.fixture(scope="function")
async def test_engine_and_factory():
    """Create fresh async engine and session factory for each test."""
    db_url = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(db_url, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    yield engine, session_factory
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine_and_factory):
    """Provide AsyncSession for fixtures and setup."""
    engine, session_factory = test_engine_and_factory
    
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(test_engine_and_factory):
    """Provide async HTTP client with monkeypatched database."""
    from app.main import app
    from httpx import AsyncClient
    
    engine, session_factory = test_engine_and_factory
    
    # Monkeypatch database functions to use test engine
    import app.core.database as db_module
    original_get_engine = db_module.get_engine
    original_get_session_factory = db_module.get_async_session_factory
    
    db_module.get_engine = lambda: engine
    db_module.get_async_session_factory = lambda: session_factory
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    finally:
        # Restore originals
        db_module.get_engine = original_get_engine
        db_module.get_async_session_factory = original_get_session_factory
        app.dependency_overrides.clear()
