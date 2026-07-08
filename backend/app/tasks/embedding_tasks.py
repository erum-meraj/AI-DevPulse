import asyncio

from app.core.logging import get_logger
from app.db.session import task_scoped_session
from app.services.embedding_service import EmbeddingService
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.embedding_tasks.generate_embeddings")
def generate_embeddings() -> dict[str, int]:
    result = asyncio.run(_generate_embeddings())
    from app.tasks.clustering_tasks import cluster_articles

    cluster_articles.delay()
    return result


async def _generate_embeddings() -> dict[str, int]:
    async with task_scoped_session() as session:
        service = EmbeddingService(session)
        result = await service.embed_pending_articles()
    logger.info("generate_embeddings_completed", result=result)
    return result
