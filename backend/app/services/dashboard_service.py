from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    DASHBOARD_TOP_CLUSTER_LIMIT,
    TREND_HIGHLIGHT_LIMIT,
)
from app.models.cluster import StoryCluster
from app.models.daily_brief import DailyBrief
from app.models.trend import Trend
from app.repositories.cluster_repo import ClusterRepository
from app.repositories.daily_brief_repo import DailyBriefRepository
from app.repositories.trend_repo import TrendRepository


@dataclass(frozen=True)
class DashboardData:
    brief: DailyBrief | None
    top_clusters: list[StoryCluster]
    trend_highlights: list[Trend]


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.brief_repository = DailyBriefRepository(session)
        self.cluster_repository = ClusterRepository(session)
        self.trend_repository = TrendRepository(session)

    async def get_dashboard(self, target_date: date) -> DashboardData:
        """Return the optional brief, today's top clusters, and active trend highlights."""
        start = datetime.combine(target_date, time.min, tzinfo=UTC)
        end = start + timedelta(days=1)
        brief = await self.brief_repository.get_by_date(target_date)
        top_clusters = await self.cluster_repository.list_top_for_date(
            start, end, DASHBOARD_TOP_CLUSTER_LIMIT
        )
        trend_highlights = await self.trend_repository.list_highlights(
            TREND_HIGHLIGHT_LIMIT
        )
        return DashboardData(brief, top_clusters, trend_highlights)
