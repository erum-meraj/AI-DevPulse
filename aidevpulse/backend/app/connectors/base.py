from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel


class RawArticle(BaseModel):
    external_id: str
    title: str
    content: str
    url: str
    author: str | None = None
    score: int | None = None
    comment_count: int | None = None
    published_at: datetime


class Connector(ABC):
    """One subclass per data source (spec §5). fetch() must be idempotent —
    the ingestion service dedupes by URL, but connectors should still avoid
    re-fetching the same items unnecessarily where the source API allows it.
    """

    source_name: str

    @abstractmethod
    async def fetch(self) -> list[RawArticle]:
        ...

    async def close(self) -> None:
        """Release any connector resources."""
        return None
