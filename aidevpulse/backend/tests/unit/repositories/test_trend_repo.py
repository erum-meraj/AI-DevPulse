from datetime import UTC, datetime

import pytest

from app.repositories.trend_repo import TrendRepository


async def create_trend(repo: TrendRepository, **overrides: object):
    payload = {
        "name": "agents",
        "mentions_today": 15,
        "mentions_7d_avg": 5.0,
        "growth_rate": 2.0,
        "status": "rising",
        "updated_at": datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
    }
    payload.update(overrides)
    return await repo.create(**payload)


@pytest.mark.asyncio
async def test_create_get_update_delete_and_list(async_session) -> None:
    repo = TrendRepository(async_session)

    created = await create_trend(repo)
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "agents"

    updated = await repo.update(created, growth_rate=3.5, status="exploding")
    assert updated.growth_rate == 3.5
    assert updated.status == "exploding"

    await create_trend(repo, name="vector-db")
    page_one = await repo.list(page=1, page_size=1)
    page_two = await repo.list(page=2, page_size=1)
    assert len(page_one) == 1
    assert len(page_two) == 1

    await repo.delete(created)
    assert await repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_get_by_name(async_session) -> None:
    repo = TrendRepository(async_session)
    created = await create_trend(repo)

    fetched = await repo.get_by_name(created.name)

    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_list_by_growth_rate(async_session) -> None:
    repo = TrendRepository(async_session)
    fastest = await create_trend(repo, name="agents", growth_rate=3.0)
    await create_trend(repo, name="llm-tools", growth_rate=1.0)

    trends = await repo.list_by_growth_rate()

    assert trends[0].id == fastest.id
