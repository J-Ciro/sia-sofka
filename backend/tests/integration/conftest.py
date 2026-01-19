"""Configuration for integration tests - override fixtures to use async sessions."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base


TEST_DATABASE_URL_ASYNC = "sqlite+aiosqlite:///:memory:"
_test_engine = None
_test_session_factory = None


async def _init_test_db():
    """Initialize test database engine and session factory."""
    global _test_engine, _test_session_factory
    
    if _test_engine is None:
        _test_engine = create_async_engine(
            TEST_DATABASE_URL_ASYNC,
            echo=False,
        )
        
        # Create all tables
        async with _test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create session factory
        _test_session_factory = async_sessionmaker(
            _test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    return _test_engine, _test_session_factory


@pytest.fixture(scope="function")
async def db_session():
    """Provide AsyncSession for integration tests."""
    engine, session_factory = await _init_test_db()
    
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session):
    """Provide an async HTTP client with monkeypatched database."""
    from app.main import app
    from httpx import AsyncClient
    
    engine, session_factory = await _init_test_db()
    
    # Monkeypatch the get_db dependency to use same session factory
    async def get_db():
        async with session_factory() as session:
            yield session
    
    # Patch the module-level functions
    import app.core.database as db_module
    original_get_engine = db_module.get_engine
    original_session_factory_func = db_module.get_async_session_factory
    
    db_module.get_engine = lambda: engine
    db_module.get_async_session_factory = lambda: session_factory
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    finally:
        # Restore originals
        db_module.get_engine = original_get_engine
        db_module.get_async_session_factory = original_session_factory_func
        app.dependency_overrides.clear()
