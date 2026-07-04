import calendar
from datetime import UTC, datetime

import feedparser

from app.connectors.base import RawArticle
from app.connectors.http_base import HTTPConnector


class RSSConnector(HTTPConnector):
    feed_url: str

    async def fetch(self) -> list[RawArticle]:
        feed_text = await self._get_text(self.feed_url)
        parsed_feed = feedparser.parse(feed_text)

        articles: list[RawArticle] = []
        for entry in parsed_feed.entries:
            published_at = self._published_at_for_entry(entry)
            if published_at is None:
                continue

            url = getattr(entry, "link", None)
            title = getattr(entry, "title", None)
            external_id = getattr(entry, "id", None) or url
            if not isinstance(url, str) or not isinstance(title, str):
                continue
            if not isinstance(external_id, str):
                continue

            author = getattr(entry, "author", None)
            articles.append(
                RawArticle(
                    external_id=external_id,
                    title=title,
                    content=self._content_for_entry(entry),
                    url=url,
                    author=author if isinstance(author, str) else None,
                    published_at=published_at,
                )
            )
        return articles

    def _content_for_entry(self, entry: feedparser.FeedParserDict) -> str:
        entry_content = getattr(entry, "content", None)
        if isinstance(entry_content, list) and entry_content:
            first_item = entry_content[0]
            value = first_item.get("value")
            if isinstance(value, str) and value.strip():
                return value

        summary = getattr(entry, "summary", None)
        if isinstance(summary, str) and summary.strip():
            return summary

        title = getattr(entry, "title", None)
        return title if isinstance(title, str) else ""

    def _published_at_for_entry(self, entry: feedparser.FeedParserDict) -> datetime | None:
        published = getattr(entry, "published_parsed", None) or getattr(
            entry, "updated_parsed", None
        )
        if published is None:
            return None
        return datetime.fromtimestamp(calendar.timegm(published), tz=UTC)
