from app.models.paper import Paper
from app.repositories.paper_repo import PaperRelevanceWeightRepository
from sqlalchemy.ext.asyncio import AsyncSession


class PaperScoringService:
    """Scores papers by summing PaperRelevanceWeight.weight for each
    weighted keyword that appears as a substring in the paper's title +
    summary text (case-insensitive). Originally designed around
    HuggingFace's ai_keywords field, but that field was confirmed empty
    on 100% of sampled papers via the live API as of 2026-08 -- title/
    summary substring matching is what's actually used. Unmatched
    keywords contribute 0, not a default of 1 -- a paper with no overlap
    with tracked interests should score low, not artificially high from
    unmatched-keyword padding."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.weight_repo = PaperRelevanceWeightRepository(session)

    async def score_paper(self, paper: Paper, weights: dict[str, float] | None = None) -> float:
        if weights is None:
            weights = await self.weight_repo.get_all_weights()
        if not weights:
            return 0.0

        searchable_text = f"{paper.title} {paper.summary or ''}".lower()
        score = 0.0
        for keyword, weight in weights.items():
            if keyword in searchable_text:
                score += weight
        return score
