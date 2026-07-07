from datetime import date as date_type

from sqlalchemy import desc, select

from app.models.daily_brief import DailyBrief
from app.repositories.base import BaseRepository


class DailyBriefRepository(BaseRepository[DailyBrief]):
    model = DailyBrief

    async def get_by_date(self, brief_date: date_type) -> DailyBrief | None:
        result = await self.session.execute(
            select(DailyBrief).where(DailyBrief.date == brief_date)
        )
        return result.scalar_one_or_none()

    async def get_latest(self, limit: int = 7) -> list[DailyBrief]:
        result = await self.session.execute(
            select(DailyBrief).order_by(desc(DailyBrief.date)).limit(limit)
        )
        return list(result.scalars().all())

    async def upsert_by_date(
        self, brief_date: date_type, **kwargs: object
    ) -> DailyBrief:
        brief = await self.get_by_date(brief_date)
        if brief is None:
            return await self.create(date=brief_date, **kwargs)
        return await self.update(brief, **kwargs)
