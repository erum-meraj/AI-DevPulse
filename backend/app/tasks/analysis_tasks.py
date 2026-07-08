import asyncio

from app.core.logging import get_logger
from app.db import model_registry  # noqa: F401
from app.db.session import task_scoped_session
from app.repositories.article_repo import ArticleRepository
from app.repositories.cluster_repo import ClusterRepository
from app.services.analysis_service import AnalysisService
from app.services.ranking_service import RankingService
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.analysis_tasks.analyze_and_rank_clusters")
def analyze_and_rank_clusters() -> dict[str, int]:
    result = asyncio.run(_analyze_and_rank_clusters())
    from app.tasks.trend_tasks import update_trends

    update_trends.delay()
    return result


async def _analyze_and_rank_clusters() -> dict[str, int]:
    async with task_scoped_session() as session:
        cluster_repo = ClusterRepository(session)
        article_repo = ArticleRepository(session)
        analysis_service = AnalysisService(session)
        ranking_service = RankingService(session)

        clusters = await cluster_repo.get_recently_updated(within_days=1)
        analyzed = 0
        skipped = 0

        for cluster in clusters:
            members = await article_repo.list_by_cluster_id(cluster.id)
            if not members:
                skipped += 1
                continue
            await analysis_service.analyze_cluster(cluster, members)
            await session.commit()
            await ranking_service.rank_cluster(cluster)
            await session.commit()
            analyzed += 1

    logger.info("analyze_and_rank_clusters_completed", analyzed=analyzed, skipped=skipped)
    return {"analyzed": analyzed, "skipped": skipped}
