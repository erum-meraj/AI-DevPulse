from bs4 import BeautifulSoup
from langdetect import detect_langs
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD,
    MAX_CONTENT_CHARS_FOR_EMBEDDING,
)
from app.models.article import Article


class NormalizationService:
    """Normalize ingested article content and drop non-English rows."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def normalize_article(self, article: Article) -> bool:
        normalized_content = self._normalize_content(article.content)
        if not normalized_content:
            normalized_content = article.title

        if not self._is_supported_english(normalized_content):
            await self.session.delete(article)
            await self.session.flush()
            return False

        article.content = normalized_content
        article.status = "normalized"
        await self.session.flush()
        return True

    def _normalize_content(self, content: str) -> str:
        text = BeautifulSoup(content, "html.parser").get_text(separator=" ", strip=True)
        collapsed = " ".join(text.split())
        return collapsed[:MAX_CONTENT_CHARS_FOR_EMBEDDING]

    def _is_supported_english(self, content: str) -> bool:
        try:
            candidates = detect_langs(content)
        except Exception:
            return False

        for candidate in candidates:
            if (
                candidate.lang == "en"
                and candidate.prob >= LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD
            ):
                return True
        return False
