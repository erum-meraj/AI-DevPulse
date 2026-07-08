from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "local"),
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a request-scoped async DB session."""
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def task_scoped_session() -> AsyncGenerator[AsyncSession, None]:
    """For use inside Celery tasks only (each task runs its own asyncio.run()
    event loop, so the module-level `engine` singleton's pooled connections —
    bound to whatever loop was active when first opened — become invalid
    across separate asyncio.run() calls in the same worker process). This
    creates a fresh engine scoped to the current task's event loop, and
    disposes it when the task completes, avoiding stale pooled connections
    bound to a closed loop. Do not use this in FastAPI request handlers —
    use get_db for those, which shares one long-lived engine correctly since
    it stays within a single running event loop."""
    task_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=(settings.ENVIRONMENT == "local"),
        pool_pre_ping=True,
    )
    task_session_factory = async_sessionmaker(
        bind=task_engine, class_=AsyncSession, expire_on_commit=False
    )
    try:
        async with task_session_factory() as session:
            yield session
    finally:
        await task_engine.dispose()
