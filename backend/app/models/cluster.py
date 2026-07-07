import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text

from app.core.constants import EMBEDDING_DIMENSIONS
from app.db.base import Base


class StoryCluster(Base):
    __tablename__ = "story_clusters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    cluster_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    why_it_matters: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True)
    discussion_count: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    # read_now | weekend | ignore
    action: Mapped[str | None] = mapped_column(String(20), nullable=True)

    centroid_embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
