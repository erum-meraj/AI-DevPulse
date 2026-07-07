from dataclasses import dataclass
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.daily_brief import DailyBrief
from app.repositories.daily_brief_repo import DailyBriefRepository


@dataclass(frozen=True)
class WeeklyReport:
    briefs: list[DailyBrief]
    stories_analyzed: int
    stories_filtered: int
    stories_selected: int
    avg_read_time_minutes: float


class DailyBriefService:
    def __init__(self, session: AsyncSession):
        self.repository = DailyBriefRepository(session)

    async def get_for_date(self, brief_date: date) -> DailyBrief:
        """Return the requested brief or raise the shared not-found error."""
        brief = await self.repository.get_by_date(brief_date)
        if brief is None:
            raise NotFoundError(
                f"Daily brief for {brief_date.isoformat()} was not found."
            )
        return brief

    async def get_optional_for_date(self, brief_date: date) -> DailyBrief | None:
        """Return the requested brief when present, otherwise None for dashboard use."""
        return await self.repository.get_by_date(brief_date)

    async def get_weekly_report(self) -> WeeklyReport:
        """Aggregate up to seven available briefs without padding missing dates."""
        newest_first = await self.repository.get_latest(limit=7)
        briefs = list(reversed(newest_first))
        count = len(briefs)
        return WeeklyReport(
            briefs=briefs,
            stories_analyzed=sum(brief.stories_analyzed or 0 for brief in briefs),
            stories_filtered=sum(brief.stories_filtered or 0 for brief in briefs),
            stories_selected=sum(brief.stories_selected or 0 for brief in briefs),
            avg_read_time_minutes=round(
                sum(brief.estimated_read_time_minutes or 0 for brief in briefs) / count,
                1,
            )
            if count
            else 0.0,
        )
