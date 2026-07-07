import math
from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def from_page(
        cls, items: list[T], page: int, page_size: int, total: int
    ) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=math.ceil(total / page_size),
        )


class ClusterSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    cluster_summary: str | None
    why_it_matters: str | None
    importance: float | None
    confidence: str | None
    sentiment: str | None
    discussion_count: int
    action: str | None
    created_at: datetime
    updated_at: datetime
