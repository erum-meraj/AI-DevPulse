import feedparser
import calendar
from datetime import datetime, UTC, timedelta

feeds = {
    "openai": "https://openai.com/news/rss.xml",
    "huggingface": "https://huggingface.co/blog/feed.xml",
    "anthropic": "https://raw.githubusercontent.com/taobojlen/anthropic-rss-feed/main/anthropic_news_rss.xml",
}

cutoff = datetime.now(UTC) - timedelta(hours=72)
print("Cutoff:", cutoff)
print()

for name, url in feeds.items():
    parsed = feedparser.parse(url)
    print(f"--- {name} ({len(parsed.entries)} entries) ---")
    for entry in parsed.entries[:3]:
        published = getattr(entry, "published_parsed", None) or getattr(
            entry, "updated_parsed", None
        )
        if published:
            dt = datetime.fromtimestamp(calendar.timegm(published), tz=UTC)
            print(f"  {dt} (passes filter: {dt >= cutoff})  -  {getattr(entry, 'title', '?')[:60]}")
        else:
            print("  NO DATE FOUND")
