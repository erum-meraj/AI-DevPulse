import pytest
import respx
from httpx import Response

from app.connectors.anthropic_rss import AnthropicRSSConnector
from app.connectors.huggingface_rss import HuggingFaceRSSConnector
from app.connectors.openai_rss import OpenAIRSSConnector
from app.core.constants import (
    ANTHROPIC_RSS_FEED_URL,
    HUGGINGFACE_RSS_FEED_URL,
    OPENAI_RSS_FEED_URL,
)

RSS_FEED_WITH_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Feed</title>
    <item>
      <title>Launch update</title>
      <link>https://example.com/launch-update</link>
      <guid>launch-update-1</guid>
      <author>team@example.com (Team)</author>
      <pubDate>Fri, 04 Jul 2026 12:00:00 GMT</pubDate>
      <description>Short summary</description>
      <content:encoded><![CDATA[<p>Full body</p>]]></content:encoded>
    </item>
  </channel>
</rss>
"""

RSS_FEED_WITH_SUMMARY_ONLY = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Feed</title>
    <item>
      <title>Summary only post</title>
      <link>https://example.com/summary-only</link>
      <guid>summary-only-1</guid>
      <pubDate>Fri, 04 Jul 2026 13:00:00 GMT</pubDate>
      <description>This becomes the content.</description>
    </item>
  </channel>
</rss>
"""


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("connector_cls", "feed_url"),
    [
        (OpenAIRSSConnector, OPENAI_RSS_FEED_URL),
        (AnthropicRSSConnector, ANTHROPIC_RSS_FEED_URL),
        (HuggingFaceRSSConnector, HUGGINGFACE_RSS_FEED_URL),
    ],
)
@respx.mock
async def test_rss_connector_maps_feed_entries(connector_cls, feed_url: str) -> None:
    respx.get(feed_url).mock(return_value=Response(200, text=RSS_FEED_WITH_CONTENT))

    connector = connector_cls()
    articles = await connector.fetch()
    await connector.close()

    assert len(articles) == 1
    article = articles[0]
    assert article.external_id == "launch-update-1"
    assert article.title == "Launch update"
    assert article.content == "<p>Full body</p>"
    assert article.url == "https://example.com/launch-update"


@pytest.mark.asyncio
@respx.mock
async def test_rss_connector_falls_back_to_summary_content() -> None:
    respx.get(OPENAI_RSS_FEED_URL).mock(return_value=Response(200, text=RSS_FEED_WITH_SUMMARY_ONLY))

    connector = OpenAIRSSConnector()
    articles = await connector.fetch()
    await connector.close()

    assert len(articles) == 1
    assert articles[0].content == "This becomes the content."
