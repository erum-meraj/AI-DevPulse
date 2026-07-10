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
