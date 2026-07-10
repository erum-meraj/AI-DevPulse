from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.topic_repo import TopicRepository
from app.schemas.topic import TopicFrequency

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/top", response_model=list[TopicFrequency])
async def get_top_topics(
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=20)] = 3,
    lookback_days: Annotated[int, Query(ge=1, le=30)] = 7,
) -> list[TopicFrequency]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    rows = await TopicRepository(session).get_top_by_mentions(start, end, limit)
    return [TopicFrequency(name=topic.name, mention_count=count) for topic, count in rows]
