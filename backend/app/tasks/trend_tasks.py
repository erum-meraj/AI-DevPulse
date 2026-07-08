import asyncio

from app.core.logging import get_logger
from app.db.session import task_scoped_session
from app.services.trend_service import TrendService
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.trend_tasks.update_trends")
def update_trends() -> int:
    result = asyncio.run(_update_trends())
    logger.info("update_trends_completed", trend_count=result)
    return result


async def _update_trends() -> int:
    async with task_scoped_session() as session:
        trends = await TrendService(session).update_trends()
    return len(trends)
