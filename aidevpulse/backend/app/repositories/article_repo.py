from sqlalchemy import select

from app.models.article import Article
from app.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[Article]):
    model = Article

    async def get_by_url(self, url: str) -> Article | None:
        result = await self.session.execute(select(Article).where(Article.url == url))
        return result.scalar_one_or_none()

    async def get_by_status(self, status: str, limit: int = 200) -> list[Article]:
        result = await self.session.execute(
            select(Article).where(Article.status == status).limit(limit)
        )
        return list(result.scalars().all())

    async def get_unembedded(self, limit: int = 200) -> list[Article]:
        return await self.get_by_status("normalized", limit=limit)

    async def get_unclustered(self, limit: int = 200) -> list[Article]:
        return await self.get_by_status("embedded", limit=limit)

    async def list_by_cluster_id(self, cluster_id) -> list[Article]:
        result = await self.session.execute(
            select(Article)
            .where(Article.cluster_id == cluster_id)
            .order_by(Article.published_at.asc())
        )
        return list(result.scalars().all())
