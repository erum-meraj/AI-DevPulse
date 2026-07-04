import uuid
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Shared CRUD operations. Table-specific repos subclass this and add
    their own query methods (e.g. get_by_url). Repositories never contain
    business logic — that belongs in services (spec §3 layering rule).
    """

    model: type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get_by_id(self, obj_id: uuid.UUID) -> ModelType | None:
        return await self.session.get(self.model, obj_id)

    async def update(self, obj: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.session.flush()
        return obj

    async def delete(self, obj: ModelType) -> None:
        await self.session.delete(obj)
        await self.session.flush()

    async def list(self, page: int = 1, page_size: int = 20) -> list[ModelType]:
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(self.model).offset(offset).limit(page_size)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(self.model))
        return int(result.scalar_one())
