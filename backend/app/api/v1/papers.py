from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.constants import PAPER_MIN_UPVOTES_FOR_TOP
from app.repositories.paper_repo import PaperRepository
from app.schemas.paper import PaperSummary

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("/top", response_model=list[PaperSummary])
async def get_top_papers(
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 5,
    min_upvotes: Annotated[int, Query(ge=0)] = PAPER_MIN_UPVOTES_FOR_TOP,
) -> list[PaperSummary]:
    papers = await PaperRepository(session).list_top_by_relevance_with_min_upvotes(
        min_upvotes, limit
    )
    return [PaperSummary.model_validate(p) for p in papers]
