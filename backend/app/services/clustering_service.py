from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import CLUSTER_SIMILARITY_THRESHOLD
from app.models.article import Article
from app.models.cluster import StoryCluster
from app.repositories.article_repo import ArticleRepository
from app.repositories.cluster_repo import ClusterRepository


class ClusteringService:
    """Assign embedded articles to an existing cluster or create a new one."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.article_repository = ArticleRepository(session)
        self.cluster_repository = ClusterRepository(session)

    async def cluster_pending_articles(self, limit: int = 200) -> dict[str, int]:
        articles = await self.article_repository.get_unclustered(limit=limit)
        clustered = 0
        created = 0

        for article in articles:
            created_new_cluster = await self.assign_cluster(article)
            clustered += 1
            if created_new_cluster:
                created += 1

        await self.session.commit()
        return {"clustered": clustered, "created": created}

    async def assign_cluster(self, article: Article) -> bool:
        if article.embedding is None:
            raise ValueError("Article must be embedded before clustering.")

        (
            nearest_cluster,
            similarity,
        ) = await self.cluster_repository.find_nearest_by_embedding(article.embedding)
        if nearest_cluster is not None and similarity is not None:
            if similarity >= CLUSTER_SIMILARITY_THRESHOLD:
                article.cluster_id = nearest_cluster.id
                await self.session.flush()
                await self._update_existing_cluster(nearest_cluster)
                article.status = "clustered"
                await self.session.flush()
                return False

        await self._create_new_cluster(article)
        article.status = "clustered"
        await self.session.flush()
        return True

    async def _update_existing_cluster(self, cluster: StoryCluster) -> None:
        member_articles = await self.article_repository.list_by_cluster_id(cluster.id)
        cluster.centroid_embedding = self.compute_centroid(
            [
                member.embedding
                for member in member_articles
                if member.embedding is not None
            ]
        )
        cluster.discussion_count = len(member_articles)
        cluster.updated_at = datetime.now(UTC)
        await self.session.flush()

    async def _create_new_cluster(self, article: Article) -> StoryCluster:
        cluster = await self.cluster_repository.create(
            title=article.title,
            centroid_embedding=article.embedding,
            discussion_count=1,
            updated_at=datetime.now(UTC),
        )
        article.cluster_id = cluster.id
        await self.session.flush()
        return cluster

    def compute_centroid(self, embeddings: list[list[float]]) -> list[float]:
        if not embeddings:
            raise ValueError("Cannot compute a centroid without embeddings.")

        dimensions = len(embeddings[0])
        totals = [0.0] * dimensions
        for embedding in embeddings:
            for index, value in enumerate(embedding):
                totals[index] += value
        count = len(embeddings)
        return [total / count for total in totals]
