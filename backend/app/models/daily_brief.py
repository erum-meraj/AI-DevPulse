import uuid
from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import ARRAY, Date, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class BriefNarrative(BaseModel):
    summary: str = Field(..., description="2-3 paragraph narrative covering today's major themes")


class DailyBrief(Base):
    __tablename__ = "daily_briefs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    date: Mapped[date_type] = mapped_column(Date, nullable=False, unique=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_read_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stories_analyzed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stories_filtered: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stories_selected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    top_cluster_ids: Mapped[list[uuid.UUID] | None] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
