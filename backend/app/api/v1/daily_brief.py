from datetime import date, datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas.daily_brief import (
    DailyBriefSummary,
    WeeklyReportResponse,
    WeeklyTotals,
)
from app.services.daily_brief_service import DailyBriefService

router = APIRouter(tags=["daily briefs"])


def current_local_date() -> date:
    return datetime.now(ZoneInfo(get_settings().TIMEZONE)).date()


@router.get("/daily-brief", response_model=DailyBriefSummary)
async def get_daily_brief(
    session: Annotated[AsyncSession, Depends(get_db)],
    brief_date: Annotated[date | None, Query(alias="date")] = None,
) -> DailyBriefSummary:
    brief = await DailyBriefService(session).get_for_date(
        brief_date or current_local_date()
    )
    return DailyBriefSummary.model_validate(brief)


@router.get("/weekly-report", response_model=WeeklyReportResponse)
async def get_weekly_report(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> WeeklyReportResponse:
    report = await DailyBriefService(session).get_weekly_report()
    return WeeklyReportResponse(
        briefs=[DailyBriefSummary.model_validate(brief) for brief in report.briefs],
        totals=WeeklyTotals(
            stories_analyzed=report.stories_analyzed,
            stories_filtered=report.stories_filtered,
            stories_selected=report.stories_selected,
            avg_read_time_minutes=report.avg_read_time_minutes,
        ),
    )
