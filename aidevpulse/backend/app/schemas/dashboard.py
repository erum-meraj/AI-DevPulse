from pydantic import BaseModel

from app.schemas.cluster import ClusterSummary
from app.schemas.daily_brief import DailyBriefSummary
from app.schemas.trend import TrendSummary


class DashboardResponse(BaseModel):
    brief: DailyBriefSummary | None
    top_clusters: list[ClusterSummary]
    trend_highlights: list[TrendSummary]
