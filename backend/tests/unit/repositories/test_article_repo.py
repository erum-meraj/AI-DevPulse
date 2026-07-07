from datetime import UTC, datetime

import pytest

from backend.app.models.article import ArticleSource
from backend.app.repositories.article_repo import ArticleRepository


async def create_article(repo: ArticleRepository, **overrides: object):
    payload = {
        "title": "Alpha release",
        "content": "Full article body",
        "url": "https://example.com/articles/alpha",
        "source": ArticleSource.OPENAI.value,
        "external_id": "alpha-1",
        "author": "DevPulse",
        "score": 42,
        "comment_count": 7,
        "published_at": datetime(2026, 7, 4, 8, 0, tzinfo=UTC),
        "status": "pending",
    }
    payload.update(overrides)
    return await repo.create(**payload)


@pytest.mark.asyncio
async def test_create_get_update_delete_and_list(async_session) -> None:
    repo = ArticleRepository(async_session)

    created = await create_article(repo)
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.url == "https://example.com/articles/alpha"

    updated = await repo.update(created, title="Updated title", status="normalized")
    assert updated.title == "Updated title"
    assert updated.status == "normalized"

    await create_article(
        repo,
        title="Beta release",
        url="https://example.com/articles/beta",
        external_id="beta-1",
        published_at=datetime(2026, 7, 4, 9, 0, tzinfo=UTC),
    )
    page_one = await repo.list(page=1, page_size=1)
    page_two = await repo.list(page=2, page_size=1)
    assert len(page_one) == 1
    assert len(page_two) == 1

    await repo.delete(created)
    assert await repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_get_by_url(async_session) -> None:
    repo = ArticleRepository(async_session)
    created = await create_article(repo)

    fetched = await repo.get_by_url(created.url)

    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_get_by_status(async_session) -> None:
    repo = ArticleRepository(async_session)
    await create_article(
        repo, url="https://example.com/pending", external_id="pending-1"
    )
    await create_article(
        repo,
        url="https://example.com/normalized",
        external_id="normalized-1",
        status="normalized",
    )

    pending = await repo.get_by_status("pending")

    assert [article.url for article in pending] == ["https://example.com/pending"]


@pytest.mark.asyncio
async def test_get_unembedded(async_session) -> None:
    repo = ArticleRepository(async_session)
    normalized = await create_article(
        repo,
        url="https://example.com/normalized",
        external_id="normalized-2",
        status="normalized",
    )
    await create_article(
        repo,
        url="https://example.com/embedded",
        external_id="embedded-1",
        status="embedded",
    )

    articles = await repo.get_unembedded()

    assert [article.id for article in articles] == [normalized.id]


@pytest.mark.asyncio
async def test_get_unclustered(async_session) -> None:
    repo = ArticleRepository(async_session)
    embedded = await create_article(
        repo,
        url="https://example.com/embedded",
        external_id="embedded-2",
        status="embedded",
    )
    await create_article(
        repo,
        url="https://example.com/clustered",
        external_id="clustered-1",
        status="clustered",
    )

    articles = await repo.get_unclustered()

    assert [article.id for article in articles] == [embedded.id]
