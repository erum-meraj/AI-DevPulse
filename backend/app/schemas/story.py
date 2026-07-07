from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.cluster import ClusterSummary


class ArticleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    summary: str | None
    url: str
    source: str
    author: str | None
    score: int | None
    comment_count: int | None
    published_at: datetime
    importance: float | None
    confidence: str | None
    status: str


class StoryDetail(ClusterSummary):
    member_articles: list[ArticleSummary]
