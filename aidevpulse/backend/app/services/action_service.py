from typing import Literal

from app.core.constants import IMPORTANCE_READ_NOW_THRESHOLD, IMPORTANCE_WEEKEND_THRESHOLD
from app.models.cluster import StoryCluster

Action = Literal["read_now", "weekend", "ignore"]


def recommend_action(importance: float) -> Action:
    """Map an importance score to the strict action thresholds from spec §10."""
    if importance > IMPORTANCE_READ_NOW_THRESHOLD:
        return "read_now"
    if importance > IMPORTANCE_WEEKEND_THRESHOLD:
        return "weekend"
    return "ignore"


class ActionService:
    def apply(self, cluster: StoryCluster, importance: float) -> Action:
        """Set and return the recommended action for a ranked cluster."""
        action = recommend_action(importance)
        cluster.action = action
        return action
