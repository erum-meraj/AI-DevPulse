import asyncio

from app.core.logging import get_logger
from app.db import model_registry  # noqa: F401
from app.db.session import task_scoped_session
from app.repositories.cluster_repo import ClusterRepository
from app.services.ranking_service import RankingService
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.ranking_tasks.re_rank_recent_clusters")
def re_rank_recent_clusters() -> dict[str, int]:
    result = asyncio.run(_re_rank_recent_clusters())
    from app.tasks.brief_tasks import generate_daily_brief

    generate_daily_brief.delay()
    return result


async def _re_rank_recent_clusters() -> dict[str, int]:
    """Re-runs RankingService.rank_cluster() against every cluster updated
    in the last 7 days. Importance scores (including the freshness
    component) are otherwise only computed once, at initial analysis time,
    and never decay -- this periodic sweep is what makes freshness actually
    decay over time as designed, and is what keeps /stories?sort_by=importance
    from permanently favoring old clusters over newer ones. Runs once daily,
    chained directly before generate_daily_brief, so the brief always
    reflects freshly-recalculated importance rather than racing it on a
    separate schedule."""
    async with task_scoped_session() as session:
        cluster_repo = ClusterRepository(session)
        ranking_service = RankingService(session)

        clusters = await cluster_repo.get_recently_updated(within_days=7)
        re_ranked = 0

        for cluster in clusters:
            await ranking_service.rank_cluster(cluster)
            await session.commit()
            re_ranked += 1

    logger.info("re_rank_recent_clusters_completed", re_ranked=re_ranked)
    return {"re_ranked": re_ranked}
