from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db
from app.schemas.cluster import ClusterSummary, PaginatedResponse
from app.services.story_service import StoryService, StorySort

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get(
    "",
    response_model=PaginatedResponse[ClusterSummary],
    description="Alias of /stories using the same underlying cluster query.",
)
async def list_clusters(
    pagination: Annotated[PaginationParams, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
    sort_by: Annotated[StorySort, Query()] = "importance",
) -> PaginatedResponse[ClusterSummary]:
    page = await StoryService(session).list_stories(
        pagination.page, pagination.page_size, sort_by
    )
    items = [ClusterSummary.model_validate(cluster) for cluster in page.items]
    return PaginatedResponse[ClusterSummary].from_page(
        items, pagination.page, pagination.page_size, page.total
    )
