from app.connectors.rss_base import RSSConnector
from app.core.constants import ANTHROPIC_RSS_FEED_URL, SOURCE_ANTHROPIC


class AnthropicRSSConnector(RSSConnector):
    source_name = SOURCE_ANTHROPIC
    feed_url = ANTHROPIC_RSS_FEED_URL
