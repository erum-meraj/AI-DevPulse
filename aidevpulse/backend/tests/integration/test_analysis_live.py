import os

import pytest

from app.core.constants import ANALYSIS_MODEL
from app.schemas.analysis import ClusterAnalysis
from app.services.ai_provider import AIProvider


@pytest.mark.integration
@pytest.mark.live
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_AI_TESTS") != "1",
    reason="Set RUN_LIVE_AI_TESTS=1 to make the real AICredits/DeepSeek API call.",
)
async def test_analysis_contract_live() -> None:
    result = await AIProvider().complete_structured(
        prompt=(
            "Analyze this article as an AI news cluster: Anthropic released Claude "
            "Code, a new agentic coding tool that lets developers delegate multi-step "
            "coding tasks from the command line. Early users report significant "
            "productivity gains on refactoring and test-writing tasks. The announcement "
            "generated significant discussion among software engineers on Hacker News."
        ),
        response_model=ClusterAnalysis,
        model=ANALYSIS_MODEL,
    )

    assert isinstance(result, ClusterAnalysis)
    assert result.topics
