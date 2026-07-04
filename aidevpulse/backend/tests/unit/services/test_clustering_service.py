from datetime import UTC, datetime

import pytest

from app.models.article import ArticleSource
from app.repositories.article_repo import ArticleRepository
from app.repositories.cluster_repo import ClusterRepository
from app.services.clustering_service import ClusteringService


def padded_vector(*values: float) -> list[float]:
    vector = [0.0] * 1536
    for index, value in enumerate(values):
        vector[index] = value
    return vector


@pytest.mark.asyncio
async def test_clustering_service_groups_near_duplicates_and_splits_unrelated(
    async_session,
) -> None:
    repo = ArticleRepository(async_session)
    first = await repo.create(
        title="OpenAI ships a new coding model",
        content="First article",
        url="https://example.com/cluster-first",
        source=ArticleSource.OPENAI.value,
        external_id="cluster-first",
        published_at=datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
        status="embedded",
        embedding=padded_vector(1.0, 0.0, 0.0),
    )
    second = await repo.create(
        title="A very similar OpenAI coding model story",
        content="Second article",
        url="https://example.com/cluster-second",
        source=ArticleSource.OPENAI.value,
        external_id="cluster-second",
        published_at=datetime(2026, 7, 4, 12, 5, tzinfo=UTC),
        status="embedded",
        embedding=padded_vector(0.9, 0.1, 0.0),
    )
    third = await repo.create(
        title="Completely unrelated infrastructure story",
        content="Third article",
        url="https://example.com/cluster-third",
        source=ArticleSource.OPENAI.value,
        external_id="cluster-third",
        published_at=datetime(2026, 7, 4, 12, 10, tzinfo=UTC),
        status="embedded",
        embedding=padded_vector(0.0, 1.0, 0.0),
    )

    service = ClusteringService(async_session)
    await service.assign_cluster(first)
    await service.assign_cluster(second)
    await service.assign_cluster(third)

    cluster_repo = ClusterRepository(async_session)
    clusters = await cluster_repo.list()

    assert first.cluster_id == second.cluster_id
    assert first.cluster_id != third.cluster_id
    assert len(clusters) == 2


@pytest.mark.asyncio
async def test_clustering_service_computes_exact_centroid(async_session) -> None:
    service = ClusteringService(async_session)

    centroid = service.compute_centroid(
        [
            padded_vector(1.0, 0.0, 0.0),
            padded_vector(0.0, 1.0, 0.0),
            padded_vector(0.0, 0.0, 1.0),
        ]
    )

    assert centroid[:3] == [1 / 3, 1 / 3, 1 / 3]
    assert all(value == 0.0 for value in centroid[3:])
