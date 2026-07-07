from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.v1.daily_brief import current_local_date
from app.schemas.cluster import ClusterSummary
from app.schemas.daily_brief import DailyBriefSummary
from app.schemas.dashboard import DashboardResponse
from app.schemas.trend import TrendSummary
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> DashboardResponse:
    dashboard = await DashboardService(session).get_dashboard(current_local_date())
    return DashboardResponse(
        brief=(
            DailyBriefSummary.model_validate(dashboard.brief)
            if dashboard.brief is not None
            else None
        ),
        top_clusters=[
            ClusterSummary.model_validate(cluster) for cluster in dashboard.top_clusters
        ],
        trend_highlights=[
            TrendSummary.model_validate(trend) for trend in dashboard.trend_highlights
        ],
    )
