from datetime import UTC, date, datetime, timedelta

import pytest

from app.models.article import ArticleSource
from app.repositories.article_repo import ArticleRepository
from app.repositories.cluster_repo import ClusterRepository
from app.schemas.analysis import ClusterAnalysis
from app.services.analysis_service import AnalysisService
from app.services.ranking_service import RankingService
from app.services.trend_service import TrendService


class PipelineAnalysisProvider:
    async def complete_structured(self, **kwargs) -> ClusterAnalysis:
        return ClusterAnalysis(
            summary="A major AI provider released a new coding model.",
            why_it_matters="The release improves production coding-agent capability.",
            signals=["Official release", "Strong discussion"],
            developer_impact={
                "ai_engineers": "high",
                "backend": "high",
                "researchers": "medium",
            },
            confidence="very_high",
            sentiment="positive",
            topics=["coding agents"],
        )


@pytest.mark.asyncio
async def test_raw_cluster_reaches_importance_and_action_checkpoint(async_session) -> None:
    now = datetime(2026, 7, 4, 12, tzinfo=UTC)
    cluster = await ClusterRepository(async_session).create(title="New coding model")
    article_repo = ArticleRepository(async_session)
    articles = []
    for index, score in enumerate((280, 220)):
        articles.append(
            await article_repo.create(
                title=f"Coding model report {index + 1}",
                content="A detailed report about a newly released AI coding model.",
                url=f"https://example.com/pipeline-{index}",
                source=ArticleSource.OPENAI.value,
                score=score,
                published_at=now - timedelta(minutes=index * 10),
                cluster_id=cluster.id,
                status="clustered",
            )
        )

    analysis = await AnalysisService(async_session, PipelineAnalysisProvider()).analyze_cluster(
        cluster, articles
    )
    trends = await TrendService(async_session).update_trends(as_of=date(2026, 7, 4))
    importance = await RankingService(async_session).rank_cluster(cluster, now=now)

    assert analysis.topics == ["coding agents"]
    assert trends[0].growth_rate == 2.0
    assert importance == pytest.approx(100.0)
    assert cluster.action == "read_now"
    assert all(article.status == "ranked" for article in articles)
