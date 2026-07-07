import math
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    FRESHNESS_DECAY_HOURS,
    POPULARITY_NORMALIZATION_CAP,
    RANKING_WEIGHTS,
    SOURCE_SCORE,
)
from app.models.article import Article
from app.models.cluster import StoryCluster
from app.repositories.article_repo import ArticleRepository
from app.repositories.trend_repo import TrendRepository
from app.services.action_service import ActionService
from app.services.trend_service import trend_score_for_cluster


class RankingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.article_repository = ArticleRepository(session)
        self.trend_repository = TrendRepository(session)
        self.action_service = ActionService()

    async def rank_cluster(
        self, cluster: StoryCluster, now: datetime | None = None
    ) -> float:
        """Calculate and persist importance, action, and ranked member statuses."""
        members = await self.article_repository.list_by_cluster_id(cluster.id)
        if not members:
            raise ValueError("Cannot rank a cluster without member articles.")
        trends = await self.trend_repository.list_for_cluster(cluster.id)
        importance = self.calculate_importance(
            members, trend_score_for_cluster(trends), now
        )

        cluster.importance = importance
        self.action_service.apply(cluster, importance)
        for article in members:
            article.importance = importance
            article.status = "ranked"
        await self.session.flush()
        return importance

    def calculate_importance(
        self,
        members: list[Article],
        trend_score: float,
        now: datetime | None = None,
    ) -> float:
        """Return the deterministic 0..100 weighted score from spec §8."""
        if not members:
            raise ValueError("Cannot rank a cluster without member articles.")

        source_score = max(SOURCE_SCORE[article.source] for article in members)
        popularity_score = min(
            sum(article.score or 0 for article in members)
            / POPULARITY_NORMALIZATION_CAP,
            1.0,
        )
        current_time = now or datetime.now(UTC)
        most_recent = max(article.published_at for article in members)
        hours_since_published = max(
            0.0, (current_time - most_recent).total_seconds() / 3600
        )
        freshness_score = math.exp(-hours_since_published / FRESHNESS_DECAY_HOURS)

        return (
            source_score * RANKING_WEIGHTS["source"]
            + popularity_score * RANKING_WEIGHTS["popularity"]
            + trend_score * RANKING_WEIGHTS["trend"]
            + freshness_score * RANKING_WEIGHTS["freshness"]
        ) * 100
