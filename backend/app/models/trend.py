import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Trend(Base):
    __tablename__ = "trends"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    mentions_today: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mentions_7d_avg: Mapped[float | None] = mapped_column(Float, nullable=True)
    growth_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    # exploding | rising | stable | declining
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
