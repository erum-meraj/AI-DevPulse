from datetime import UTC, datetime

import pytest
import respx
from httpx import Response

from backend.app.connectors.hackernews import HackerNewsConnector
from backend.app.core.constants import (
    HACKERNEWS_ITEM_URL_TEMPLATE,
    HACKERNEWS_NEW_STORIES_URL,
    HACKERNEWS_TOP_STORIES_URL,
)


@pytest.mark.asyncio
@respx.mock
async def test_hackernews_connector_filters_to_ai_relevant_items() -> None:
    respx.get(HACKERNEWS_TOP_STORIES_URL).mock(return_value=Response(200, json=[101]))
    respx.get(HACKERNEWS_NEW_STORIES_URL).mock(return_value=Response(200, json=[102]))
    respx.get(HACKERNEWS_ITEM_URL_TEMPLATE.format(item_id=101)).mock(
        return_value=Response(
            200,
            json={
                "id": 101,
                "type": "story",
                "title": "New OpenAI model reaches production",
                "url": "https://example.com/openai-model",
                "by": "alice",
                "score": 150,
                "descendants": 22,
                "time": 1783152000,
                "text": "<p>Launch details</p>",
            },
        )
    )
    respx.get(HACKERNEWS_ITEM_URL_TEMPLATE.format(item_id=102)).mock(
        return_value=Response(
            200,
            json={
                "id": 102,
                "type": "story",
                "title": "Weekend gardening notes",
                "url": "https://example.com/gardening",
                "by": "bob",
                "score": 12,
                "descendants": 1,
                "time": 1783152060,
            },
        )
    )

    connector = HackerNewsConnector()
    articles = await connector.fetch()
    await connector.close()

    assert len(articles) == 1
    article = articles[0]
    assert article.external_id == "101"
    assert article.url == "https://example.com/openai-model"
    assert article.author == "alice"
    assert article.score == 150
    assert article.comment_count == 22
    assert article.published_at == datetime.fromtimestamp(1783152000, tz=UTC)
