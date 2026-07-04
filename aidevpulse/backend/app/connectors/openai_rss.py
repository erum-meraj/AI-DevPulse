from app.connectors.rss_base import RSSConnector
from app.core.constants import OPENAI_RSS_FEED_URL, SOURCE_OPENAI


class OpenAIRSSConnector(RSSConnector):
    source_name = SOURCE_OPENAI
    feed_url = OPENAI_RSS_FEED_URL
