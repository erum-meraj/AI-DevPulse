from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TrendSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    mentions_today: int | None
    mentions_7d_avg: float | None
    growth_rate: float | None
    status: str | None
    updated_at: datetime
