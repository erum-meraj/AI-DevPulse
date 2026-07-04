from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    ANALYSIS_MAX_ARTICLES,
    ANALYSIS_MAX_INPUT_CHARS,
    ANALYSIS_MODEL,
)
from app.models.article import Article
from app.models.cluster import StoryCluster
from app.repositories.topic_repo import TopicRepository
from app.schemas.analysis import ClusterAnalysis
from app.services.ai_provider import AIProvider

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


class AnalysisService:
    def __init__(self, session: AsyncSession, ai_provider: AIProvider | None = None):
        self.session = session
        self.ai_provider = ai_provider or AIProvider()
        self.topic_repository = TopicRepository(session)

    async def analyze_cluster(
        self, cluster: StoryCluster, member_articles: list[Article]
    ) -> ClusterAnalysis:
        """Analyze members with an LLM and persist cluster fields, topics, and statuses."""
        if not member_articles:
            raise ValueError("Cannot analyze a cluster without member articles.")

        prompt = self.build_prompt(member_articles)
        analysis = await self.ai_provider.complete_structured(
            prompt=prompt,
            response_model=ClusterAnalysis,
            model=ANALYSIS_MODEL,
        )

        cluster.cluster_summary = analysis.summary
        cluster.why_it_matters = analysis.why_it_matters
        cluster.confidence = analysis.confidence
        cluster.sentiment = analysis.sentiment

        topics = self.normalize_topics(analysis.topics)
        for article in member_articles:
            article.status = "analyzed"
            existing_topics = await self.topic_repository.list_for_article(article.id)
            for existing_topic in existing_topics:
                if existing_topic.name not in topics:
                    await self.topic_repository.remove_article_topic(article.id, existing_topic.id)
            for topic_name in topics:
                topic = await self.topic_repository.get_or_create(topic_name)
                await self.topic_repository.add_article_topic_if_missing(article.id, topic.id)

        await self.session.flush()
        return analysis

    def build_prompt(self, member_articles: list[Article]) -> str:
        """Load prompt templates and render the highest-scoring articles within the input cap."""
        templates = [
            (PROMPT_DIR / "summarize.md").read_text(encoding="utf-8"),
            (PROMPT_DIR / "why_it_matters.md").read_text(encoding="utf-8"),
        ]
        template = "\n\n".join(templates)
        selected = sorted(member_articles, key=lambda article: article.score or 0, reverse=True)[
            :ANALYSIS_MAX_ARTICLES
        ]
        context_budget = max(0, ANALYSIS_MAX_INPUT_CHARS - len(template))
        article_context = self._format_articles(selected, context_budget)
        return template.format(articles=article_context)

    def _format_articles(self, articles: list[Article], char_budget: int) -> str:
        blocks: list[str] = []
        remaining = char_budget
        for index, article in enumerate(articles, start=1):
            prefix = f"[{index}] {article.title}\n"
            if remaining <= len(prefix):
                break
            content = article.content[: remaining - len(prefix)]
            block = f"{prefix}{content}"
            blocks.append(block)
            remaining -= len(block) + 2
        return "\n\n".join(blocks)

    def normalize_topics(self, topics: list[str]) -> list[str]:
        """Return unique, non-empty lowercase topic names while preserving order."""
        return list(dict.fromkeys(topic.strip().lower() for topic in topics if topic.strip()))
