import math
from datetime import UTC, datetime, timedelta

import pytest

from backend.app.models.article import Article, ArticleSource
from backend.app.services.ranking_service import RankingService


def article(source: ArticleSource, score: int, published_at: datetime) -> Article:
    return Article(
        title="Ranked article",
        content="Body",
        url=f"https://example.com/{source}-{score}",
        source=source.value,
        score=score,
        published_at=published_at,
    )


def test_calculate_importance_uses_spec_formula() -> None:
    now = datetime(2026, 7, 4, 12, tzinfo=UTC)
    members = [
        article(ArticleSource.HACKERNEWS, 300, now - timedelta(hours=48)),
        article(ArticleSource.OPENAI, 200, now - timedelta(hours=24)),
    ]
    service = RankingService.__new__(RankingService)

    score = service.calculate_importance(members, trend_score=0.75, now=now)

    expected = (1.0 * 0.3 + 1.0 * 0.3 + 0.75 * 0.2 + math.exp(-1) * 0.2) * 100
    assert score == pytest.approx(expected)


def test_calculate_importance_clamps_future_article_age() -> None:
    now = datetime(2026, 7, 4, 12, tzinfo=UTC)
    members = [article(ArticleSource.OPENAI, 0, now + timedelta(minutes=5))]

    score = RankingService.__new__(RankingService).calculate_importance(
        members, trend_score=0.0, now=now
    )

    assert score == pytest.approx(50.0)
