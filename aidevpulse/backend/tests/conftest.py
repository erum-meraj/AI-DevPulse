import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/aidevpulse"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.core.config import get_settings
from app.db.model_registry import Base
from tests.factories import ArticleFactory, ClusterFactory, DailyBriefFactory, TrendFactory

settings = get_settings()


@pytest_asyncio.fixture
async def engine():
    """Function-scoped: a fresh engine (and NullPool, so no connection is
    reused across event loops) per test. pytest-asyncio creates a new event
    loop per test function by default; asyncpg connections are bound to the
    loop that created them, so a session-scoped engine breaks on the second
    test. Function-scoping the engine keeps engine lifetime == loop lifetime.
    """
    eng = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def async_session(engine):
    """Rollback-per-test: wraps the whole test in one transaction and rolls
    it back at the end, so no data survives between tests.
    """
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        yield session
        await session.close()
        await trans.rollback()


@pytest.fixture
def model_factory(async_session):
    async def create(factory_class, **overrides):
        instance = factory_class.build(**overrides)
        async_session.add(instance)
        await async_session.flush()
        return instance

    return create


@pytest.fixture
def sample_cluster_factory(model_factory):
    async def create(**overrides):
        return await model_factory(ClusterFactory, **overrides)

    return create


@pytest.fixture
def sample_article_factory(model_factory):
    async def create(**overrides):
        return await model_factory(ArticleFactory, **overrides)

    return create


@pytest.fixture
def sample_trend_factory(model_factory):
    async def create(**overrides):
        return await model_factory(TrendFactory, **overrides)

    return create


@pytest.fixture
def sample_daily_brief_factory(model_factory):
    async def create(**overrides):
        return await model_factory(DailyBriefFactory, **overrides)

    return create
