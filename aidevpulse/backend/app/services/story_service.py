from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.article import Article
from app.models.cluster import StoryCluster
from app.repositories.article_repo import ArticleRepository
from app.repositories.cluster_repo import ClusterRepository

StorySort = Literal["importance", "created_at"]


@dataclass(frozen=True)
class StoryPage:
    items: list[StoryCluster]
    total: int


@dataclass(frozen=True)
class StoryWithMembers:
    cluster: StoryCluster
    member_articles: list[Article]


class StoryService:
    def __init__(self, session: AsyncSession):
        self.cluster_repository = ClusterRepository(session)
        self.article_repository = ArticleRepository(session)

    async def list_stories(
        self, page: int, page_size: int, sort_by: StorySort
    ) -> StoryPage:
        """Return one sorted cluster page and the unpaginated row count."""
        items = await self.cluster_repository.list_sorted(sort_by, page, page_size)
        return StoryPage(items=items, total=await self.cluster_repository.count())

    async def get_story(self, cluster_id: UUID) -> StoryWithMembers:
        """Return a cluster with members, or raise the shared not-found error."""
        cluster = await self.cluster_repository.get_by_id(cluster_id)
        if cluster is None:
            raise NotFoundError(f"Story cluster {cluster_id} was not found.")
        members = await self.article_repository.list_by_cluster_id(cluster_id)
        return StoryWithMembers(cluster=cluster, member_articles=members)
