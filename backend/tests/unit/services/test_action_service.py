import pytest

from backend.app.services.action_service import recommend_action


@pytest.mark.parametrize(
    ("importance", "expected"),
    [(90.01, "read_now"), (90.0, "weekend"), (70.01, "weekend"), (70.0, "ignore")],
)
def test_recommend_action_uses_strict_thresholds(
    importance: float, expected: str
) -> None:
    assert recommend_action(importance) == expected
