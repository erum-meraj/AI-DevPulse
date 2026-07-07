import uuid

from sqlalchemy import desc, select

from app.models.article import Article
from app.models.topic import ArticleTopic, Topic
from app.models.trend import Trend
from app.repositories.base import BaseRepository


class TrendRepository(BaseRepository[Trend]):
    model = Trend

    async def get_by_name(self, name: str) -> Trend | None:
        result = await self.session.execute(select(Trend).where(Trend.name == name))
        return result.scalar_one_or_none()

    async def upsert_by_name(self, name: str, **kwargs: object) -> Trend:
        trend = await self.get_by_name(name)
        if trend is None:
            return await self.create(name=name, **kwargs)
        return await self.update(trend, **kwargs)

    async def list_for_cluster(self, cluster_id: uuid.UUID) -> list[Trend]:
        result = await self.session.execute(
            select(Trend)
            .join(Topic, Topic.name == Trend.name)
            .join(ArticleTopic, ArticleTopic.topic_id == Topic.id)
            .join(Article, Article.id == ArticleTopic.article_id)
            .where(Article.cluster_id == cluster_id)
            .distinct()
            .order_by(desc(Trend.growth_rate), Trend.name.asc())
        )
        return list(result.scalars().all())

    async def list_by_growth_rate(
        self, page: int = 1, page_size: int = 20
    ) -> list[Trend]:
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Trend)
            .order_by(desc(Trend.growth_rate), Trend.name.asc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all())

    async def list_highlights(self, limit: int) -> list[Trend]:
        result = await self.session.execute(
            select(Trend)
            .where(Trend.status.in_(("exploding", "rising")))
            .order_by(desc(Trend.growth_rate), Trend.name.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
