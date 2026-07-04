from datetime import date

import pytest

from app.models.trend import Trend
from app.services.trend_service import (
    TrendService,
    normalize_growth_rate,
    trend_score_for_cluster,
)


@pytest.mark.parametrize(
    ("growth_rate", "expected"),
    [(-2.0, 0.0), (0.4, 0.4), (1.0, 1.0), (8.0, 1.0), (None, 0.0)],
)
def test_normalize_growth_rate_clips_to_ranking_range(growth_rate, expected) -> None:
    assert normalize_growth_rate(growth_rate) == expected


def test_trend_score_uses_max_individual_score_and_empty_default() -> None:
    trends = [Trend(name="declining", growth_rate=-0.5), Trend(name="hot", growth_rate=8.0)]

    assert trend_score_for_cluster(trends) == 1.0
    assert trend_score_for_cluster([]) == 0.0


@pytest.mark.parametrize(
    ("growth_rate", "expected"),
    [
        (2.01, "exploding"),
        (2.0, "rising"),
        (0.51, "rising"),
        (0.5, "stable"),
        (-0.3, "stable"),
        (-0.31, "declining"),
    ],
)
def test_status_for_growth_rate_boundaries(growth_rate: float, expected: str) -> None:
    assert TrendService.status_for_growth_rate(growth_rate) == expected


@pytest.mark.asyncio
async def test_update_trends_uses_seven_day_average(async_session) -> None:
    from datetime import UTC, datetime

    from app.models.article import ArticleSource
    from app.repositories.article_repo import ArticleRepository
    from app.repositories.cluster_repo import ClusterRepository
    from app.repositories.topic_repo import TopicRepository
    from app.repositories.trend_repo import TrendRepository

    target = date(2026, 7, 4)
    cluster = await ClusterRepository(async_session).create(title="Agents")
    article_repo = ArticleRepository(async_session)
    topic_repo = TopicRepository(async_session)
    topic = await topic_repo.create(name="agents")
    timestamps = [datetime(2026, 7, 3, 12, tzinfo=UTC)] * 7 + [
        datetime(2026, 7, 4, hour, tzinfo=UTC) for hour in range(4)
    ]
    for index, published_at in enumerate(timestamps):
        article = await article_repo.create(
            title=f"Agent article {index}",
            content="Body",
            url=f"https://example.com/trend-{index}",
            source=ArticleSource.HACKERNEWS.value,
            published_at=published_at,
            cluster_id=cluster.id,
            status="analyzed",
        )
        await topic_repo.add_article_topic(article.id, topic.id)

    await TrendService(async_session).update_trends(as_of=target)
    trend = await TrendRepository(async_session).get_by_name("agents")

    assert trend is not None
    assert trend.mentions_today == 4
    assert trend.mentions_7d_avg == 1.0
    assert trend.growth_rate == 3.0
    assert trend.status == "exploding"
