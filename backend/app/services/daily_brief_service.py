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
        self.session = session
        self.repository = DailyBriefRepository(session)

    async def get_for_date(self, brief_date: date) -> DailyBrief:
        """Return the requested brief or raise the shared not-found error."""
        brief = await self.repository.get_by_date(brief_date)
        if brief is None:
            raise NotFoundError(f"Daily brief for {brief_date.isoformat()} was not found.")
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

    async def generate_for_date(self, brief_date: date) -> DailyBrief:
        """Generate (or regenerate) the daily brief for brief_date. Idempotent: upserts by date."""
        from datetime import datetime, timedelta, timezone

        from app.core.constants import DAILY_BRIEF_MINUTES_PER_STORY, DAILY_BRIEF_TOP_N
        from app.repositories.article_repo import ArticleRepository
        from app.repositories.cluster_repo import ClusterRepository
        from app.schemas.daily_brief import BriefNarrative
        from app.services.ai_provider import AIProvider

        start = datetime.combine(brief_date, datetime.min.time(), tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        cluster_repo = ClusterRepository(self.session)
        article_repo = ArticleRepository(self.session)

        top_clusters = await cluster_repo.list_top_for_date(start, end, DAILY_BRIEF_TOP_N)
        stories_selected = len(top_clusters)
        stories_analyzed = await article_repo.count_published_between(start, end)
        stories_filtered = max(0, stories_analyzed - stories_selected)

        summary = await self._generate_narrative(top_clusters)

        return await self.repository.upsert_by_date(
            brief_date,
            summary=summary,
            top_cluster_ids=[c.id for c in top_clusters],
            stories_analyzed=stories_analyzed,
            stories_filtered=stories_filtered,
            stories_selected=stories_selected,
            estimated_read_time_minutes=max(
                1, round(stories_selected * DAILY_BRIEF_MINUTES_PER_STORY)
            ),
        )

    async def _generate_narrative(self, top_clusters: list) -> str:
        """Call the LLM once for an overall narrative summary. Returns empty string if no clusters."""
        if not top_clusters:
            return ""

        from pathlib import Path

        from app.core.constants import ANALYSIS_MODEL
        from app.schemas.daily_brief import BriefNarrative
        from app.services.ai_provider import AIProvider

        template = (Path(__file__).parent.parent / "prompts" / "daily_brief.md").read_text()
        story_summaries = "\n\n".join(
            f"- {c.title}: {c.cluster_summary or c.why_it_matters or ''}" for c in top_clusters
        )
        prompt = template.format(story_count=len(top_clusters), story_summaries=story_summaries)

        result = await AIProvider().complete_structured(
            prompt=prompt, response_model=BriefNarrative, model=ANALYSIS_MODEL
        )
        return result.summary
