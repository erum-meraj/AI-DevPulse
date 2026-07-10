import httpx
from datetime import datetime, timezone

from app.core.constants import HTTP_TIMEOUT_SECONDS, HTTP_USER_AGENT
from app.core.logging import get_logger

logger = get_logger(__name__)

HF_DAILY_PAPERS_API_URL = "https://huggingface.co/api/daily_papers"


class HuggingFacePapersConnector:
    """Fetches today's papers from HuggingFace's internal daily_papers API
    (no official public API, no auth required as of 2026-07 -- if this
    silently starts returning empty/errors, check whether HF has changed
    or locked down this endpoint, same caution as the Anthropic RSS
    situation documented elsewhere in this codebase)."""

    async def fetch_papers(self) -> list[dict]:
        async with httpx.AsyncClient(
            timeout=HTTP_TIMEOUT_SECONDS, headers={"User-Agent": HTTP_USER_AGENT}
        ) as client:
            response = await client.get(HF_DAILY_PAPERS_API_URL)
            response.raise_for_status()
            raw_papers = response.json()

        logger.info("huggingface_papers_fetched", count=len(raw_papers))
        return [self._normalize(entry) for entry in raw_papers]

    def _normalize(self, entry: dict) -> dict:
        paper = entry.get("paper", {})
        published_raw = paper.get("publishedAt") or entry.get("publishedAt")
        published_at = (
            datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
            if published_raw
            else datetime.now(timezone.utc)
        )
        arxiv_id = paper.get("id", "")
        url = (
            f"https://huggingface.co/papers/{arxiv_id}" if arxiv_id else entry.get("thumbnail", "")
        )

        return {
            "arxiv_id": arxiv_id,
            "title": entry.get("title") or paper.get("title", ""),
            "summary": paper.get("ai_summary") or entry.get("summary") or paper.get("summary"),
            "url": url,
            "published_at": published_at,
            "upvotes": paper.get("upvotes"),
            "github_stars": paper.get("githubStars"),
            "ai_keywords": [k.lower() for k in (paper.get("ai_keywords") or [])],
        }
