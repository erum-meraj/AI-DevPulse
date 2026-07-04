import os

import pytest

from app.core.constants import ANALYSIS_MODEL
from app.schemas.analysis import ClusterAnalysis
from app.services.ai_provider import AIProvider


@pytest.mark.integration
@pytest.mark.live
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_AI_TESTS") != "1",
    reason="Set RUN_LIVE_AI_TESTS=1 to make the real Anthropic API call.",
)
async def test_anthropic_analysis_contract_live() -> None:
    result = await AIProvider().complete_structured(
        prompt=(
            "Analyze this article as an AI news cluster: A provider released a faster "
            "coding model for software engineers."
        ),
        response_model=ClusterAnalysis,
        model=ANALYSIS_MODEL,
    )

    assert isinstance(result, ClusterAnalysis)
    assert result.topics
