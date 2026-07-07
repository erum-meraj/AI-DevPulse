from backend.app.core.constants import ANALYSIS_MAX_RETRIES
from backend.app.schemas.analysis import ClusterAnalysis
from backend.app.services.ai_provider import AIProvider


class FakeCompletions:
    def __init__(self) -> None:
        self.kwargs = {}

    async def create(self, **kwargs):
        self.kwargs = kwargs
        return ClusterAnalysis(
            summary="Summary",
            why_it_matters="Impact",
            signals=["Official release"],
            developer_impact={
                "ai_engineers": "high",
                "backend": "medium",
                "researchers": "medium",
            },
            confidence="high",
            sentiment="positive",
            topics=["agents"],
        )


class FakeChat:
    def __init__(self) -> None:
        self.completions = FakeCompletions()


class FakeStructuredClient:
    def __init__(self) -> None:
        self.chat = FakeChat()


async def test_complete_structured_uses_response_model_and_two_retries() -> None:
    client = FakeStructuredClient()
    provider = AIProvider(structured_client=client)

    result = await provider.complete_structured(
        "Analyze this", ClusterAnalysis, "test-model"
    )

    assert isinstance(result, ClusterAnalysis)
    assert client.chat.completions.kwargs["response_model"] is ClusterAnalysis
    assert client.chat.completions.kwargs["max_retries"] == ANALYSIS_MAX_RETRIES
    assert client.chat.completions.kwargs["model"] == "test-model"
