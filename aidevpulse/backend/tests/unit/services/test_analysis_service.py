from datetime import UTC, datetime

import pytest

from app.core.constants import ANALYSIS_MAX_ARTICLES, ANALYSIS_MAX_INPUT_CHARS, ANALYSIS_MODEL
from app.models.article import Article, ArticleSource
from app.repositories.article_repo import ArticleRepository
from app.repositories.cluster_repo import ClusterRepository
from app.repositories.topic_repo import TopicRepository
from app.schemas.analysis import ClusterAnalysis
from app.services.analysis_service import AnalysisService


class FakeAnalysisProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.topics = [" Coding Agents ", "Model Releases", "coding agents"]

    async def complete_structured(self, **kwargs) -> ClusterAnalysis:
        self.calls.append(kwargs)
        return ClusterAnalysis(
            summary="Anthropic released a faster coding model. Engineers are evaluating it.",
            why_it_matters="The model may reduce coding-agent latency and operating cost.",
            signals=["Official release", "HN trending"],
            developer_impact={
                "ai_engineers": "high",
                "backend": "medium",
                "researchers": "medium",
            },
            confidence="very_high",
            sentiment="positive",
            topics=self.topics,
        )


async def make_clustered_article(article_repo, cluster_id, index: int, score: int) -> Article:
    return await article_repo.create(
        title=f"Article {index}",
        content=f"Content for article {index}. " * 100,
        url=f"https://example.com/analysis-{index}",
        source=ArticleSource.ANTHROPIC.value,
        external_id=f"analysis-{index}",
        score=score,
        published_at=datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
        cluster_id=cluster_id,
        status="clustered",
    )


@pytest.mark.asyncio
async def test_analyze_cluster_persists_fields_statuses_and_topics(async_session) -> None:
    cluster = await ClusterRepository(async_session).create(title="Coding model")
    article_repo = ArticleRepository(async_session)
    articles = [
        await make_clustered_article(article_repo, cluster.id, 1, 80),
        await make_clustered_article(article_repo, cluster.id, 2, 120),
    ]
    provider = FakeAnalysisProvider()

    analysis = await AnalysisService(async_session, provider).analyze_cluster(cluster, articles)

    assert cluster.cluster_summary == analysis.summary
    assert cluster.why_it_matters == analysis.why_it_matters
    assert cluster.confidence == "very_high"
    assert cluster.sentiment == "positive"
    assert all(article.status == "analyzed" for article in articles)
    assert provider.calls[0]["model"] == ANALYSIS_MODEL
    topics = await TopicRepository(async_session).list_for_article(articles[0].id)
    assert [topic.name for topic in topics] == ["coding agents", "model releases"]

    provider.topics = ["coding agents"]
    await AnalysisService(async_session, provider).analyze_cluster(cluster, articles)
    topics_after_rerun = await TopicRepository(async_session).list_for_article(articles[0].id)
    assert [topic.name for topic in topics_after_rerun] == ["coding agents"]


def test_build_prompt_samples_highest_scores_and_caps_input() -> None:
    articles = [
        Article(
            title=f"Article {index}",
            content="x" * 10_000,
            url=f"https://example.com/prompt-{index}",
            source=ArticleSource.OPENAI.value,
            score=index,
            published_at=datetime(2026, 7, 4, tzinfo=UTC),
        )
        for index in range(ANALYSIS_MAX_ARTICLES + 2)
    ]
    service = AnalysisService.__new__(AnalysisService)

    prompt = service.build_prompt(articles)

    assert len(prompt) <= ANALYSIS_MAX_INPUT_CHARS
    assert f"Article {ANALYSIS_MAX_ARTICLES + 1}" in prompt
    assert "Article 0\n" not in prompt
