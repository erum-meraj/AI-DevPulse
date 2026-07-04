from datetime import date

import pytest

from app.repositories.daily_brief_repo import DailyBriefRepository


async def create_daily_brief(repo: DailyBriefRepository, **overrides: object):
    payload = {
        "date": date(2026, 7, 4),
        "summary": "Top AI stories",
        "estimated_read_time_minutes": 8,
        "stories_analyzed": 20,
        "stories_filtered": 12,
        "stories_selected": 8,
        "top_cluster_ids": [],
    }
    payload.update(overrides)
    return await repo.create(**payload)


@pytest.mark.asyncio
async def test_create_get_update_delete_and_list(async_session) -> None:
    repo = DailyBriefRepository(async_session)

    created = await create_daily_brief(repo)
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.date == date(2026, 7, 4)

    updated = await repo.update(created, summary="Updated summary", stories_selected=6)
    assert updated.summary == "Updated summary"
    assert updated.stories_selected == 6

    await create_daily_brief(repo, date=date(2026, 7, 5))
    page_one = await repo.list(page=1, page_size=1)
    page_two = await repo.list(page=2, page_size=1)
    assert len(page_one) == 1
    assert len(page_two) == 1

    await repo.delete(created)
    assert await repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_get_by_date(async_session) -> None:
    repo = DailyBriefRepository(async_session)
    created = await create_daily_brief(repo)

    fetched = await repo.get_by_date(created.date)

    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_get_latest(async_session) -> None:
    repo = DailyBriefRepository(async_session)
    await create_daily_brief(repo, date=date(2026, 7, 2), summary="Older")
    latest = await create_daily_brief(repo, date=date(2026, 7, 4), summary="Latest")

    briefs = await repo.get_latest(limit=1)

    assert [brief.id for brief in briefs] == [latest.id]


@pytest.mark.asyncio
async def test_upsert_by_date(async_session) -> None:
    repo = DailyBriefRepository(async_session)

    created = await repo.upsert_by_date(date(2026, 7, 4), summary="Initial")
    updated = await repo.upsert_by_date(date(2026, 7, 4), summary="Rebuilt", stories_selected=5)

    assert updated.id == created.id
    assert updated.summary == "Rebuilt"
    assert updated.stories_selected == 5
