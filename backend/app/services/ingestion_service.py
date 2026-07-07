from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.anthropic_rss import AnthropicRSSConnector
from app.connectors.base import Connector
from app.connectors.hackernews import HackerNewsConnector
from app.connectors.huggingface_rss import HuggingFaceRSSConnector
from app.connectors.openai_rss import OpenAIRSSConnector
from app.repositories.article_repo import ArticleRepository
from app.services.normalization_service import NormalizationService


def get_default_connectors() -> list[Connector]:
    return [
        HackerNewsConnector(),
        OpenAIRSSConnector(),
        AnthropicRSSConnector(),
        HuggingFaceRSSConnector(),
    ]


class IngestionService:
    """Fetch raw articles from connectors, dedupe by URL, and persist new rows."""

    def __init__(
        self, session: AsyncSession, connectors: Sequence[Connector] | None = None
    ):
        self.session = session
        self.article_repository = ArticleRepository(session)
        self.normalization_service = NormalizationService(session)
        self.connectors = (
            list(connectors) if connectors is not None else get_default_connectors()
        )

    async def collect_articles(self) -> dict[str, int]:
        counts: dict[str, int] = {
            connector.source_name: 0 for connector in self.connectors
        }

        try:
            for connector in self.connectors:
                raw_articles = await connector.fetch()
                for raw_article in raw_articles:
                    existing = await self.article_repository.get_by_url(raw_article.url)
                    if existing is not None:
                        continue

                    article = await self.article_repository.create(
                        title=raw_article.title,
                        content=raw_article.content,
                        url=raw_article.url,
                        source=connector.source_name,
                        external_id=raw_article.external_id,
                        author=raw_article.author,
                        score=raw_article.score,
                        comment_count=raw_article.comment_count,
                        published_at=raw_article.published_at,
                        status="pending",
                    )
                    if await self.normalization_service.normalize_article(article):
                        counts[connector.source_name] += 1
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        finally:
            for connector in self.connectors:
                await connector.close()

        return counts
