from datetime import UTC, datetime

import pytest

from backend.app.connectors.base import Connector, RawArticle
from backend.app.repositories.article_repo import ArticleRepository
from backend.app.services.ingestion_service import IngestionService


class StubConnector(Connector):
    def __init__(self, source_name: str, articles: list[RawArticle]):
        self.source_name = source_name
        self._articles = articles

    async def fetch(self) -> list[RawArticle]:
        return list(self._articles)


@pytest.mark.asyncio
async def test_ingestion_service_dedupes_seen_urls(async_session) -> None:
    raw_article = RawArticle(
        external_id="item-1",
        title="OpenAI releases update",
        content=(
            "<p>This article explains how OpenAI shipped a new model for software "
            "engineers.</p>"
        ),
        url="https://example.com/story-1",
        author="team",
        published_at=datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
    )
    service = IngestionService(
        async_session, connectors=[StubConnector("openai", [raw_article])]
    )

    first_counts = await service.collect_articles()
    second_counts = await service.collect_articles()

    repo = ArticleRepository(async_session)
    articles = await repo.list()

    assert first_counts == {"openai": 1}
    assert second_counts == {"openai": 0}
    assert len(articles) == 1
    assert articles[0].status == "normalized"
