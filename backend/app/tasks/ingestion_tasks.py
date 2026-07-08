import asyncio

from app.core.logging import get_logger
from app.db.session import task_scoped_session
from app.services.ingestion_service import IngestionService
from app.tasks.celery_app import celery_app

from app.db import model_registry  # noqa: F401  (ensures all ORM models are registered before any DB operation runs)

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.ingestion_tasks.collect_articles")
def collect_articles() -> dict[str, int]:
    return asyncio.run(_collect_articles())


async def _collect_articles() -> dict[str, int]:
    async with task_scoped_session() as session:
        service = IngestionService(session)
        counts = await service.collect_articles()
    logger.info("collect_articles_completed", counts=counts)
    return counts
