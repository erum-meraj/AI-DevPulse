from datetime import UTC, date, datetime, timedelta

import factory

from app.models.article import Article, ArticleSource
from app.models.cluster import StoryCluster
from app.models.daily_brief import DailyBrief
from app.models.trend import Trend


class ClusterFactory(factory.Factory):
    class Meta:
        model = StoryCluster

    title = factory.Sequence(lambda number: f"Cluster {number}")
    cluster_summary = "A concise cluster summary."
    why_it_matters = "This matters to working software engineers."
    importance = 80.0
    confidence = "high"
    sentiment = "positive"
    discussion_count = 1
    action = "weekend"
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))


class ArticleFactory(factory.Factory):
    class Meta:
        model = Article

    title = factory.Sequence(lambda number: f"Article {number}")
    content = "Detailed article content about AI engineering."
    url = factory.Sequence(lambda number: f"https://example.com/factory-{number}")
    source = ArticleSource.OPENAI.value
    external_id = factory.Sequence(lambda number: f"factory-{number}")
    published_at = factory.LazyFunction(lambda: datetime.now(UTC))
    status = "ranked"


class TrendFactory(factory.Factory):
    class Meta:
        model = Trend

    name = factory.Sequence(lambda number: f"trend-{number}")
    mentions_today = 10
    mentions_7d_avg = 2.0
    growth_rate = 2.0
    status = "rising"
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))


class DailyBriefFactory(factory.Factory):
    class Meta:
        model = DailyBrief

    date = factory.Sequence(lambda n: date(2026, 1, 1) + timedelta(days=n))
    summary = "Today's major AI engineering developments."
    estimated_read_time_minutes = 3
    stories_analyzed = 20
    stories_filtered = 17
    stories_selected = 3
    top_cluster_ids = factory.LazyFunction(list)
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
