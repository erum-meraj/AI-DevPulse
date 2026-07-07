from datetime import UTC, datetime

import pytest

from backend.app.models.article import ArticleSource
from backend.app.repositories.article_repo import ArticleRepository
from backend.app.services.embedding_service import EmbeddingService


def make_vector(value: float) -> list[float]:
    return [value] * 1536


class FakeAIProvider:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        if len(texts) > 1:
            raise RuntimeError("batch failure")
        if "bad article" in texts[0].lower():
            raise RuntimeError("single item failure")
        return [make_vector(0.5)]


@pytest.mark.asyncio
async def test_embedding_service_isolates_failures(async_session) -> None:
    repo = ArticleRepository(async_session)
    good_article = await repo.create(
        title="Good article",
        content="A detailed English article about AI systems and developer tooling.",
        url="https://example.com/good-article",
        source=ArticleSource.OPENAI.value,
        external_id="good-article",
        published_at=datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
        status="normalized",
    )
    bad_article = await repo.create(
        title="Bad article",
        content="Another English article that will simulate an embedding failure.",
        url="https://example.com/bad-article",
        source=ArticleSource.OPENAI.value,
        external_id="bad-article",
        published_at=datetime(2026, 7, 4, 12, 5, tzinfo=UTC),
        status="normalized",
    )

    service = EmbeddingService(async_session, ai_provider=FakeAIProvider())
    result = await service.embed_articles([good_article, bad_article])

    assert result == {"processed": 1, "failed": 1}
    assert good_article.status == "embedded"
    assert good_article.embedding == make_vector(0.5)
    assert bad_article.status == "normalized"
    assert bad_article.embedding is None
