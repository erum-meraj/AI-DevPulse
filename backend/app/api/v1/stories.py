from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db
from app.schemas.cluster import ClusterSummary, PaginatedResponse
from app.schemas.story import ArticleSummary, StoryDetail
from app.services.story_service import StoryService, StorySort

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("", response_model=PaginatedResponse[ClusterSummary])
async def list_stories(
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


@router.get("/{cluster_id}", response_model=StoryDetail)
async def get_story(
    cluster_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> StoryDetail:
    story = await StoryService(session).get_story(cluster_id)
    cluster_data = ClusterSummary.model_validate(story.cluster).model_dump()
    return StoryDetail(
        **cluster_data,
        member_articles=[
            ArticleSummary.model_validate(article) for article in story.member_articles
        ],
    )
