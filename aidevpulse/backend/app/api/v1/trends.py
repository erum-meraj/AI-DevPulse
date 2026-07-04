from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db
from app.schemas.cluster import PaginatedResponse
from app.schemas.trend import TrendSummary
from app.services.trend_service import TrendService

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("", response_model=PaginatedResponse[TrendSummary])
async def list_trends(
    pagination: Annotated[PaginationParams, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> PaginatedResponse[TrendSummary]:
    page = await TrendService(session).list_trends(
        pagination.page, pagination.page_size
    )
    items = [TrendSummary.model_validate(trend) for trend in page.items]
    return PaginatedResponse[TrendSummary].from_page(
        items, pagination.page, pagination.page_size, page.total
    )
