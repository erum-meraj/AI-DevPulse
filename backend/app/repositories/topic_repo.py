import uuid
from datetime import datetime

from sqlalchemy import func, select

from app.models.article import Article
from app.models.topic import ArticleTopic, Topic
from app.repositories.base import BaseRepository


class TopicRepository(BaseRepository[Topic]):
    model = Topic

    async def get_by_name(self, name: str) -> Topic | None:
        result = await self.session.execute(select(Topic).where(Topic.name == name))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Topic]:
        result = await self.session.execute(select(Topic).order_by(Topic.name))
        return list(result.scalars().all())

    async def get_or_create(self, name: str) -> Topic:
        topic = await self.get_by_name(name)
        if topic is not None:
            return topic
        return await self.create(name=name)

    async def add_article_topic(self, article_id: uuid.UUID, topic_id: uuid.UUID) -> ArticleTopic:
        association = ArticleTopic(article_id=article_id, topic_id=topic_id)
        self.session.add(association)
        await self.session.flush()
        return association

    async def add_article_topic_if_missing(
        self, article_id: uuid.UUID, topic_id: uuid.UUID
    ) -> ArticleTopic:
        association = await self.session.get(
            ArticleTopic, {"article_id": article_id, "topic_id": topic_id}
        )
        if association is not None:
            return association
        return await self.add_article_topic(article_id, topic_id)

    async def count_mentions(self, topic_id: uuid.UUID, start: datetime, end: datetime) -> int:
        result = await self.session.execute(
            select(func.count(Article.id))
            .join(ArticleTopic, Article.id == ArticleTopic.article_id)
            .where(
                ArticleTopic.topic_id == topic_id,
                Article.cluster_id.is_not(None),
                Article.published_at >= start,
                Article.published_at < end,
            )
        )
        return int(result.scalar_one())

    async def get_top_by_mentions(
        self, start: datetime, end: datetime, limit: int = 3
    ) -> list[tuple[Topic, int]]:
        """Return the top N topics by article mention count in the given
        window, each paired with its count. Only counts articles that
        have been clustered (cluster_id is not null), matching the same
        filter used by count_mentions."""
        result = await self.session.execute(
            select(Topic, func.count(Article.id).label("mention_count"))
            .join(ArticleTopic, Topic.id == ArticleTopic.topic_id)
            .join(Article, Article.id == ArticleTopic.article_id)
            .where(
                Article.cluster_id.is_not(None),
                Article.published_at >= start,
                Article.published_at < end,
            )
            .group_by(Topic.id)
            .order_by(func.count(Article.id).desc())
            .limit(limit)
        )
        return [(row[0], row[1]) for row in result.all()]

    async def remove_article_topic(self, article_id: uuid.UUID, topic_id: uuid.UUID) -> None:
        association = await self.session.get(
            ArticleTopic, {"article_id": article_id, "topic_id": topic_id}
        )
        if association is not None:
            await self.session.delete(association)
            await self.session.flush()

    async def list_for_article(self, article_id: uuid.UUID) -> list[Topic]:
        result = await self.session.execute(
            select(Topic)
            .join(ArticleTopic, Topic.id == ArticleTopic.topic_id)
            .where(ArticleTopic.article_id == article_id)
            .order_by(Topic.name)
        )
        return list(result.scalars().all())

    async def list_articles_for_topic(self, topic_id: uuid.UUID) -> list[Article]:
        result = await self.session.execute(
            select(Article)
            .join(ArticleTopic, Article.id == ArticleTopic.article_id)
            .where(ArticleTopic.topic_id == topic_id)
            .order_by(Article.published_at.desc())
        )
        return list(result.scalars().all())
