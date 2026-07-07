from datetime import UTC, datetime

import pytest

from backend.app.models.article import ArticleSource
from backend.app.repositories.article_repo import ArticleRepository
from backend.app.repositories.topic_repo import TopicRepository


async def create_article(article_repo: ArticleRepository, **overrides: object):
    payload = {
        "title": "Topic article",
        "content": "Body",
        "url": "https://example.com/topic-article",
        "source": ArticleSource.OPENAI.value,
        "external_id": "topic-article-1",
        "published_at": datetime(2026, 7, 4, 8, 0, tzinfo=UTC),
        "status": "pending",
    }
    payload.update(overrides)
    return await article_repo.create(**payload)


async def create_topic(repo: TopicRepository, **overrides: object):
    payload = {"name": "agents", "description": "Autonomous agent systems"}
    payload.update(overrides)
    return await repo.create(**payload)


@pytest.mark.asyncio
async def test_create_get_update_delete_and_list(async_session) -> None:
    repo = TopicRepository(async_session)

    created = await create_topic(repo)
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "agents"

    updated = await repo.update(created, description="Updated description")
    assert updated.description == "Updated description"

    await create_topic(repo, name="vector-db")
    page_one = await repo.list(page=1, page_size=1)
    page_two = await repo.list(page=2, page_size=1)
    assert len(page_one) == 1
    assert len(page_two) == 1

    await repo.delete(created)
    assert await repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_get_by_name(async_session) -> None:
    repo = TopicRepository(async_session)
    created = await create_topic(repo)

    fetched = await repo.get_by_name(created.name)

    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_add_and_list_for_article(async_session) -> None:
    topic_repo = TopicRepository(async_session)
    article_repo = ArticleRepository(async_session)
    article = await create_article(article_repo)
    topic = await create_topic(topic_repo)

    association = await topic_repo.add_article_topic(article.id, topic.id)
    topics = await topic_repo.list_for_article(article.id)

    assert association.article_id == article.id
    assert [item.id for item in topics] == [topic.id]


@pytest.mark.asyncio
async def test_list_articles_for_topic(async_session) -> None:
    topic_repo = TopicRepository(async_session)
    article_repo = ArticleRepository(async_session)
    first = await create_article(
        article_repo, url="https://example.com/first", external_id="first"
    )
    second = await create_article(
        article_repo,
        url="https://example.com/second",
        external_id="second",
        published_at=datetime(2026, 7, 4, 9, 0, tzinfo=UTC),
    )
    topic = await create_topic(topic_repo)
    await topic_repo.add_article_topic(first.id, topic.id)
    await topic_repo.add_article_topic(second.id, topic.id)

    articles = await topic_repo.list_articles_for_topic(topic.id)

    assert [article.id for article in articles] == [second.id, first.id]


@pytest.mark.asyncio
async def test_remove_article_topic(async_session) -> None:
    topic_repo = TopicRepository(async_session)
    article_repo = ArticleRepository(async_session)
    article = await create_article(article_repo)
    topic = await create_topic(topic_repo)
    await topic_repo.add_article_topic(article.id, topic.id)

    await topic_repo.remove_article_topic(article.id, topic.id)

    assert await topic_repo.list_for_article(article.id) == []
