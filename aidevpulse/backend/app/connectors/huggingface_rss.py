from app.connectors.rss_base import RSSConnector
from app.core.constants import HUGGINGFACE_RSS_FEED_URL, SOURCE_HUGGINGFACE


class HuggingFaceRSSConnector(RSSConnector):
    source_name = SOURCE_HUGGINGFACE
    feed_url = HUGGINGFACE_RSS_FEED_URL
