from typing import Any, TypeVar

import instructor
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.constants import (
    ANALYSIS_MAX_OUTPUT_TOKENS,
    ANALYSIS_MAX_RETRIES,
    EMBEDDING_MODEL,
)

T = TypeVar("T")


class AIProvider:
    def __init__(
        self,
        client: AsyncOpenAI | None = None,
        structured_client: Any | None = None,
    ):
        settings = get_settings()
        self.client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.structured_client = structured_client or instructor.from_anthropic(
            AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one OpenAI embedding vector for each input string."""
        response = await self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        return [list(item.embedding) for item in response.data]

    async def complete_structured(self, prompt: str, response_model: type[T], model: str) -> T:
        """Call Anthropic through instructor and validate the response as response_model."""
        return await self.structured_client.messages.create(
            model=model,
            max_tokens=ANALYSIS_MAX_OUTPUT_TOKENS,
            messages=[{"role": "user", "content": prompt}],
            response_model=response_model,
            max_retries=ANALYSIS_MAX_RETRIES,
        )
