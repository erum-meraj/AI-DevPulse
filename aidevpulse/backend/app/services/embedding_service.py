from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import EMBEDDING_BATCH_SIZE, MAX_CONTENT_CHARS_FOR_EMBEDDING
from app.models.article import Article
from app.repositories.article_repo import ArticleRepository
from app.services.ai_provider import AIProvider


class EmbeddingService:
    """Generate embeddings for normalized articles without failing the whole batch."""

    def __init__(self, session: AsyncSession, ai_provider: AIProvider | None = None):
        self.session = session
        self.ai_provider = ai_provider or AIProvider()
        self.article_repository = ArticleRepository(session)

    async def embed_pending_articles(self, limit: int = 200) -> dict[str, int]:
        articles = await self.article_repository.get_unembedded(limit=limit)
        return await self.embed_articles(articles)

    async def embed_articles(self, articles: Sequence[Article]) -> dict[str, int]:
        processed = 0
        failed = 0

        for start in range(0, len(articles), EMBEDDING_BATCH_SIZE):
            batch = list(articles[start : start + EMBEDDING_BATCH_SIZE])
            batch_processed, batch_failed = await self._embed_batch_with_isolation(batch)
            processed += batch_processed
            failed += batch_failed

        await self.session.commit()
        return {"processed": processed, "failed": failed}

    async def _embed_batch_with_isolation(self, articles: list[Article]) -> tuple[int, int]:
        if not articles:
            return 0, 0

        texts = [self._build_embedding_text(article) for article in articles]
        try:
            embeddings = await self.ai_provider.embed(texts)
            if len(embeddings) != len(articles):
                raise ValueError("Embedding count mismatch")
        except Exception:
            return await self._embed_articles_one_by_one(articles)

        for article, embedding in zip(articles, embeddings, strict=True):
            article.embedding = embedding
            article.status = "embedded"
        await self.session.flush()
        return len(articles), 0

    async def _embed_articles_one_by_one(self, articles: list[Article]) -> tuple[int, int]:
        processed = 0
        failed = 0
        for article in articles:
            try:
                embedding = await self.ai_provider.embed([self._build_embedding_text(article)])
            except Exception:
                failed += 1
                continue

            article.embedding = embedding[0]
            article.status = "embedded"
            processed += 1

        await self.session.flush()
        return processed, failed

    def _build_embedding_text(self, article: Article) -> str:
        truncated_content = article.content[:MAX_CONTENT_CHARS_FOR_EMBEDDING]
        return f"{article.title}\n\n{truncated_content}"
