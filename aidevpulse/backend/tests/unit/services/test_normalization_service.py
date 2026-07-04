from datetime import UTC, datetime

import pytest

from app.models.article import ArticleSource
from app.repositories.article_repo import ArticleRepository
from app.services.normalization_service import NormalizationService


@pytest.mark.asyncio
async def test_normalization_service_strips_html_and_marks_article(async_session) -> None:
    repo = ArticleRepository(async_session)
    article = await repo.create(
        title="Launch update",
        content="<div><p>This article explains a major AI release for developers.</p></div>",
        url="https://example.com/normalized-article",
        source=ArticleSource.OPENAI.value,
        external_id="normalized-article",
        published_at=datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
        status="pending",
    )

    service = NormalizationService(async_session)
    kept = await service.normalize_article(article)

    assert kept is True
    assert article.content == "This article explains a major AI release for developers."
    assert article.status == "normalized"


@pytest.mark.asyncio
async def test_normalization_service_drops_non_english_article(async_session) -> None:
    repo = ArticleRepository(async_session)
    article = await repo.create(
        title="Bonjour",
        content="<p>Bonjour tout le monde, ceci est un article en francais tres court.</p>",
        url="https://example.com/french-article",
        source=ArticleSource.OPENAI.value,
        external_id="french-article",
        published_at=datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
        status="pending",
    )

    service = NormalizationService(async_session)
    kept = await service.normalize_article(article)

    assert kept is False
    assert await repo.get_by_id(article.id) is None
