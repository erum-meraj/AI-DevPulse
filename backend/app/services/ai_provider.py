from typing import Any, TypeVar

import instructor
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.constants import (
    ANALYSIS_MAX_OUTPUT_TOKENS,
    ANALYSIS_MAX_RETRIES,
)

T = TypeVar("T")


class AIProvider:
    """All AI calls (embeddings + structured analysis) route through AICredits'
    OpenAI-compatible gateway (spec §13.2). Embeddings still request
    text-embedding-3-small specifically, since the DB's pgvector column is
    fixed at 1536 dimensions (spec §4.1) — changing the embedding model's
    dimensionality would require a schema migration.
    """

    def __init__(
        self,
        client: AsyncOpenAI | None = None,
        structured_client: Any | None = None,
    ):
        settings = get_settings()
        base_client = AsyncOpenAI(
            api_key=settings.AICREDITS_API_KEY,
            base_url=settings.AICREDITS_BASE_URL,
        )
        self.client = client or base_client
        self.structured_client = structured_client or instructor.from_openai(
            base_client, mode=instructor.Mode.JSON
        )
        self._chat_model = settings.AICREDITS_CHAT_MODEL
        self._embedding_model = settings.AICREDITS_EMBEDDING_MODEL

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector for each input string, via AICredits."""
        response = await self.client.embeddings.create(
            model=self._embedding_model,
            input=texts,
        )
        return [list(item.embedding) for item in response.data]

    async def complete_structured(
        self, prompt: str, response_model: type[T], model: str | None = None
    ) -> T:
        """Call the configured chat model through instructor and validate the
        response as response_model. `model` param is kept for call-site
        compatibility but defaults to settings.AICREDITS_CHAT_MODEL if not
        explicitly overridden.
        """
        return await self.structured_client.chat.completions.create(
            model=model or self._chat_model,
            max_tokens=ANALYSIS_MAX_OUTPUT_TOKENS,
            messages=[{"role": "user", "content": prompt}],
            response_model=response_model,
            max_retries=ANALYSIS_MAX_RETRIES,
        )
