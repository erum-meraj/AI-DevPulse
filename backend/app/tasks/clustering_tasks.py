import asyncio

from app.tasks.analysis_tasks import analyze_and_rank_clusters

from app.core.logging import get_logger
from app.db.session import task_scoped_session
from app.services.clustering_service import ClusteringService
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.clustering_tasks.cluster_articles")
def cluster_articles() -> dict[str, int]:
    return asyncio.run(_cluster_articles())


async def _cluster_articles() -> dict[str, int]:
    async with task_scoped_session() as session:
        service = ClusteringService(session)
        result = await service.cluster_pending_articles()
    logger.info("cluster_articles_completed", result=result)

    analyze_and_rank_clusters.delay()
    return result
