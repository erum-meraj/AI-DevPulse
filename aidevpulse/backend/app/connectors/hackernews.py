import re
from datetime import UTC, datetime
from typing import Any

from app.connectors.base import RawArticle
from app.connectors.http_base import HTTPConnector
from app.core.constants import (
    AI_RELEVANT_KEYWORDS,
    HACKERNEWS_ITEM_URL_TEMPLATE,
    HACKERNEWS_MAX_ITEMS_PER_FETCH,
    HACKERNEWS_NEW_STORIES_URL,
    HACKERNEWS_TOP_STORIES_URL,
    SOURCE_HACKERNEWS,
)


class HackerNewsConnector(HTTPConnector):
    source_name = SOURCE_HACKERNEWS
    _keyword_pattern = re.compile(
        r"\b(?:" + "|".join(re.escape(keyword) for keyword in AI_RELEVANT_KEYWORDS) + r")\b",
        re.IGNORECASE,
    )

    async def fetch(self) -> list[RawArticle]:
        top_story_ids = await self._get_json(HACKERNEWS_TOP_STORIES_URL)
        new_story_ids = await self._get_json(HACKERNEWS_NEW_STORIES_URL)

        ordered_ids: list[int] = []
        seen_ids: set[int] = set()
        for item_id in [*top_story_ids, *new_story_ids]:
            if isinstance(item_id, int) and item_id not in seen_ids:
                seen_ids.add(item_id)
                ordered_ids.append(item_id)

        ordered_ids = ordered_ids[:HACKERNEWS_MAX_ITEMS_PER_FETCH]

        articles: list[RawArticle] = []
        for item_id in ordered_ids:
            item = await self._get_json(HACKERNEWS_ITEM_URL_TEMPLATE.format(item_id=item_id))
            article = self._to_raw_article(item)
            if article is not None:
                articles.append(article)
        return articles

    def _to_raw_article(self, payload: dict[str, Any] | None) -> RawArticle | None:
        if payload is None or payload.get("type") != "story":
            return None

        title = payload.get("title")
        url = payload.get("url")
        timestamp = payload.get("time")
        external_id = payload.get("id")
        if not isinstance(title, str) or not isinstance(url, str):
            return None
        if not isinstance(timestamp, int) or external_id is None:
            return None
        if not self._keyword_pattern.search(title):
            return None

        text = payload.get("text")
        content = text if isinstance(text, str) and text.strip() else title

        return RawArticle(
            external_id=str(external_id),
            title=title,
            content=content,
            url=url,
            author=payload.get("by"),
            score=payload.get("score"),
            comment_count=payload.get("descendants"),
            published_at=datetime.fromtimestamp(timestamp, tz=UTC),
        )
