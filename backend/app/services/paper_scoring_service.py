from app.models.paper import Paper
from app.repositories.paper_repo import PaperRelevanceWeightRepository
from sqlalchemy.ext.asyncio import AsyncSession


class PaperScoringService:
    """Scores papers by summing PaperRelevanceWeight.weight for each of a
    paper's ai_keywords that has a matching row in paper_relevance_weights.
    Unmatched keywords contribute 0, not a default of 1 -- a paper with no
    keyword overlap with tracked interests should score low, not
    artificially high from unmatched-keyword padding."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.weight_repo = PaperRelevanceWeightRepository(session)

    async def score_paper(self, paper: Paper, weights: dict[str, float] | None = None) -> float:
        if weights is None:
            weights = await self.weight_repo.get_all_weights()
        if not paper.ai_keywords:
            return 0.0
        return sum(weights.get(keyword.lower(), 0.0) for keyword in paper.ai_keywords)
