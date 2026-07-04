from typing import Literal

from pydantic import BaseModel, Field

DeveloperGroup = Literal["ai_engineers", "backend", "researchers"]
ImpactLevel = Literal["low", "medium", "high"]


class ClusterAnalysis(BaseModel):
    summary: str = Field(..., description="2-3 sentences: what happened")
    why_it_matters: str = Field(..., description="2-3 sentences: why engineers should care")
    signals: list[str] = Field(
        ...,
        description="Short reasons this was surfaced, such as an official release or trend",
    )
    developer_impact: dict[DeveloperGroup, ImpactLevel]
    confidence: Literal["low", "medium", "high", "very_high"]
    sentiment: Literal["positive", "neutral", "negative", "mixed"]
    topics: list[str] = Field(..., description="Concise normalized topics found in the cluster")
