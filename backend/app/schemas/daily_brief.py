from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DailyBriefSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    date: date
    summary: str | None
    estimated_read_time_minutes: int | None
    stories_analyzed: int | None
    stories_filtered: int | None
    stories_selected: int | None
    top_cluster_ids: list[UUID] | None
    created_at: datetime


class WeeklyTotals(BaseModel):
    stories_analyzed: int
    stories_filtered: int
    stories_selected: int
    avg_read_time_minutes: float


class WeeklyReportResponse(BaseModel):
    briefs: list[DailyBriefSummary]
    totals: WeeklyTotals
