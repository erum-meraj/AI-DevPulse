from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    TREND_EXPLODING_THRESHOLD,
    TREND_RISING_THRESHOLD,
    TREND_STABLE_LOWER_BOUND,
)
from app.models.trend import Trend
from app.repositories.topic_repo import TopicRepository
from app.repositories.trend_repo import TrendRepository


@dataclass(frozen=True)
class TrendPage:
    items: list[Trend]
    total: int


def normalize_growth_rate(growth_rate: float | None) -> float:
    """Clip a raw, potentially absent or unbounded growth rate into 0..1."""
    if growth_rate is None:
        return 0.0
    return max(0.0, min(growth_rate, 1.0))


def trend_score_for_cluster(cluster_topics: list[Trend]) -> float:
    """Return the maximum individually normalized topic trend, or zero when empty."""
    if not cluster_topics:
        return 0.0
    return max(normalize_growth_rate(trend.growth_rate) for trend in cluster_topics)


class TrendService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.topic_repository = TopicRepository(session)
        self.trend_repository = TrendRepository(session)

    async def list_trends(self, page: int, page_size: int) -> TrendPage:
        """Return one growth-sorted trend page and the unpaginated row count."""
        items = await self.trend_repository.list_by_growth_rate(page, page_size)
        return TrendPage(items=items, total=await self.trend_repository.count())

    async def update_trends(self, as_of: date | None = None) -> list[Trend]:
        """Calculate and upsert daily trend metrics for every extracted topic."""
        target_date = as_of or datetime.now(UTC).date()
        today_start = datetime.combine(target_date, time.min, tzinfo=UTC)
        tomorrow_start = today_start + timedelta(days=1)
        trailing_start = today_start - timedelta(days=7)

        updated: list[Trend] = []
        for topic in await self.topic_repository.list_all():
            mentions_today = await self.topic_repository.count_mentions(
                topic.id, today_start, tomorrow_start
            )
            trailing_mentions = await self.topic_repository.count_mentions(
                topic.id, trailing_start, today_start
            )
            mentions_7d_avg = trailing_mentions / 7
            growth_rate = (mentions_today - mentions_7d_avg) / max(mentions_7d_avg, 1)
            trend = await self.trend_repository.upsert_by_name(
                topic.name,
                mentions_today=mentions_today,
                mentions_7d_avg=mentions_7d_avg,
                growth_rate=growth_rate,
                status=self.status_for_growth_rate(growth_rate),
                updated_at=datetime.now(UTC),
            )
            updated.append(trend)

        await self.session.flush()
        return updated

    @staticmethod
    def status_for_growth_rate(growth_rate: float) -> str:
        """Classify a raw growth rate using the named thresholds from spec §9."""
        if growth_rate > TREND_EXPLODING_THRESHOLD:
            return "exploding"
        if growth_rate > TREND_RISING_THRESHOLD:
            return "rising"
        if growth_rate >= TREND_STABLE_LOWER_BOUND:
            return "stable"
        return "declining"
