from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict


class PaperSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    arxiv_id: str
    title: str
    summary: str | None
    url: str
    published_at: datetime
    upvotes: int | None
    github_stars: int | None
    ai_keywords: list[str] | None
    relevance_score: float | None
