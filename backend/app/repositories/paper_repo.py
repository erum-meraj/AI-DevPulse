import uuid
from datetime import datetime

from sqlalchemy import select

from app.models.paper import Paper, PaperRelevanceWeight
from app.repositories.base import BaseRepository


class PaperRepository(BaseRepository[Paper]):
    model = Paper

    async def get_by_arxiv_id(self, arxiv_id: str) -> Paper | None:
        result = await self.session.execute(select(Paper).where(Paper.arxiv_id == arxiv_id))
        return result.scalar_one_or_none()

    async def list_top_by_relevance(self, limit: int = 20) -> list[Paper]:
        result = await self.session.execute(
            select(Paper)
            .order_by(Paper.relevance_score.desc().nulls_last(), Paper.published_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_top_by_relevance_with_min_upvotes(
        self, min_upvotes: int, limit: int = 5
    ) -> list[Paper]:
        """Top N papers by relevance_score, restricted to papers with at
        least min_upvotes. Returns however many qualify, even if fewer
        than limit -- an empty or short result is expected and valid on
        days where few papers clear the upvote bar, not an error."""
        result = await self.session.execute(
            select(Paper)
            .where(Paper.upvotes >= min_upvotes)
            .order_by(Paper.relevance_score.desc().nulls_last(), Paper.upvotes.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class PaperRelevanceWeightRepository(BaseRepository[PaperRelevanceWeight]):
    model = PaperRelevanceWeight

    async def get_all_weights(self) -> dict[str, float]:
        result = await self.session.execute(select(PaperRelevanceWeight))
        return {row.keyword: row.weight for row in result.scalars().all()}

    async def set_weight(self, keyword: str, weight: float) -> PaperRelevanceWeight:
        existing = await self.session.get(PaperRelevanceWeight, keyword)
        if existing is None:
            return await self.create(keyword=keyword, weight=weight)
        existing.weight = weight
        await self.session.flush()
        return existing
