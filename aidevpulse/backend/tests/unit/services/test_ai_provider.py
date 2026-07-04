from app.core.constants import ANALYSIS_MAX_RETRIES
from app.schemas.analysis import ClusterAnalysis
from app.services.ai_provider import AIProvider


class FakeMessages:
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


class FakeStructuredClient:
    def __init__(self) -> None:
        self.messages = FakeMessages()


async def test_complete_structured_uses_response_model_and_two_retries() -> None:
    client = FakeStructuredClient()
    provider = AIProvider(structured_client=client)

    result = await provider.complete_structured("Analyze this", ClusterAnalysis, "test-model")

    assert isinstance(result, ClusterAnalysis)
    assert client.messages.kwargs["response_model"] is ClusterAnalysis
    assert client.messages.kwargs["max_retries"] == ANALYSIS_MAX_RETRIES
    assert client.messages.kwargs["model"] == "test-model"
