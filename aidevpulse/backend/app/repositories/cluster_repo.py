from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, exists, select, text

from app.models.article import Article
from app.models.cluster import StoryCluster
from app.repositories.base import BaseRepository


class ClusterRepository(BaseRepository[StoryCluster]):
    model = StoryCluster

    async def get_by_action(
        self, action: str, page: int = 1, page_size: int = 20
    ) -> list[StoryCluster]:
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(StoryCluster)
            .where(StoryCluster.action == action)
            .order_by(desc(StoryCluster.updated_at))
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all())

    async def list_sorted(
        self, sort_by: str = "importance", page: int = 1, page_size: int = 20
    ) -> list[StoryCluster]:
        sort_column = (
            StoryCluster.created_at if sort_by == "created_at" else StoryCluster.importance
        )
        result = await self.session.execute(
            select(StoryCluster)
            .order_by(desc(sort_column).nulls_last(), desc(StoryCluster.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all())

    async def list_top_for_date(
        self, start: datetime, end: datetime, limit: int
    ) -> list[StoryCluster]:
        has_article_on_date = exists(
            select(Article.id).where(
                Article.cluster_id == StoryCluster.id,
                Article.published_at >= start,
                Article.published_at < end,
            )
        )
        result = await self.session.execute(
            select(StoryCluster)
            .where(has_article_on_date)
            .order_by(desc(StoryCluster.importance).nulls_last())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recently_updated(self, within_days: int = 7) -> list[StoryCluster]:
        cutoff = datetime.now().astimezone() - timedelta(days=within_days)
        result = await self.session.execute(
            select(StoryCluster)
            .where(StoryCluster.updated_at >= cutoff)
            .order_by(desc(StoryCluster.updated_at))
        )
        return list(result.scalars().all())

    async def find_nearest_by_embedding(
        self, embedding: list[float], within_days: int = 7
    ) -> tuple[StoryCluster | None, float | None]:
        cutoff = datetime.now(UTC) - timedelta(days=within_days)
        vector_literal = "[" + ",".join(str(value) for value in embedding) + "]"
        result = await self.session.execute(
            text(
                """
                SELECT id, 1 - (centroid_embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM story_clusters
                WHERE updated_at >= :cutoff
                  AND centroid_embedding IS NOT NULL
                ORDER BY centroid_embedding <=> CAST(:embedding AS vector)
                LIMIT 1
                """
            ),
            {"embedding": vector_literal, "cutoff": cutoff},
        )
        row = result.first()
        if row is None:
            return None, None

        cluster = await self.get_by_id(row.id)
        if cluster is None:
            return None, None
        return cluster, float(row.similarity)
