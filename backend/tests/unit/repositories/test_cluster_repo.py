from datetime import UTC, datetime, timedelta

import pytest

from backend.app.repositories.cluster_repo import ClusterRepository


async def create_cluster(repo: ClusterRepository, **overrides: object):
    now = datetime(2026, 7, 4, 10, 0, tzinfo=UTC)
    payload = {
        "title": "Cluster Alpha",
        "cluster_summary": "Summary",
        "why_it_matters": "Why it matters",
        "importance": 88.0,
        "confidence": "high",
        "sentiment": "positive",
        "discussion_count": 1,
        "action": "read_now",
        "updated_at": now,
    }
    payload.update(overrides)
    return await repo.create(**payload)


@pytest.mark.asyncio
async def test_create_get_update_delete_and_list(async_session) -> None:
    repo = ClusterRepository(async_session)

    created = await create_cluster(repo)
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.title == "Cluster Alpha"

    updated = await repo.update(created, title="Cluster Beta", action="weekend")
    assert updated.title == "Cluster Beta"
    assert updated.action == "weekend"

    await create_cluster(repo, title="Cluster Gamma")
    page_one = await repo.list(page=1, page_size=1)
    page_two = await repo.list(page=2, page_size=1)
    assert len(page_one) == 1
    assert len(page_two) == 1

    await repo.delete(created)
    assert await repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_get_by_action(async_session) -> None:
    repo = ClusterRepository(async_session)
    selected = await create_cluster(repo, title="Read now cluster", action="read_now")
    await create_cluster(repo, title="Ignore cluster", action="ignore")

    clusters = await repo.get_by_action("read_now")

    assert [cluster.id for cluster in clusters] == [selected.id]


@pytest.mark.asyncio
async def test_get_recently_updated(async_session) -> None:
    repo = ClusterRepository(async_session)
    recent = await create_cluster(repo, title="Recent cluster")
    await create_cluster(
        repo,
        title="Old cluster",
        updated_at=datetime.now(UTC) - timedelta(days=20),
    )

    clusters = await repo.get_recently_updated(within_days=7)

    assert [cluster.id for cluster in clusters] == [recent.id]
