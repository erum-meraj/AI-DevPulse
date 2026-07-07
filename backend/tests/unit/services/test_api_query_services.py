from datetime import UTC, date, datetime, timedelta

import pytest

from backend.app.core.exceptions import NotFoundError
from backend.app.services.daily_brief_service import DailyBriefService
from backend.app.services.dashboard_service import DashboardService
from backend.app.services.story_service import StoryService
from backend.app.services.trend_service import TrendService


@pytest.mark.asyncio
async def test_story_service_returns_real_total_and_members(
    async_session, sample_cluster_factory, sample_article_factory
) -> None:
    clusters = [
        await sample_cluster_factory(importance=float(value)) for value in (10, 30, 20)
    ]
    article = await sample_article_factory(cluster_id=clusters[1].id)
    service = StoryService(async_session)

    page = await service.list_stories(page=1, page_size=2, sort_by="importance")
    detail = await service.get_story(clusters[1].id)

    assert page.total == 3
    assert [item.importance for item in page.items] == [30.0, 20.0]
    assert [item.id for item in detail.member_articles] == [article.id]


@pytest.mark.asyncio
async def test_story_service_raises_not_found(async_session) -> None:
    from uuid import uuid4

    with pytest.raises(NotFoundError):
        await StoryService(async_session).get_story(uuid4())


@pytest.mark.asyncio
async def test_weekly_report_is_chronological_aggregated_and_not_padded(
    async_session, sample_daily_brief_factory
) -> None:
    for day, read_time in ((2, 2), (4, 4), (3, 3)):
        await sample_daily_brief_factory(
            date=date(2026, 7, day),
            stories_analyzed=day,
            stories_filtered=day - 1,
            stories_selected=1,
            estimated_read_time_minutes=read_time,
        )

    report = await DailyBriefService(async_session).get_weekly_report()

    assert [brief.date.day for brief in report.briefs] == [2, 3, 4]
    assert len(report.briefs) == 3
    assert report.stories_analyzed == 9
    assert report.stories_filtered == 6
    assert report.stories_selected == 3
    assert report.avg_read_time_minutes == 3.0


@pytest.mark.asyncio
async def test_dashboard_applies_date_and_highlight_caps(
    async_session,
    sample_cluster_factory,
    sample_article_factory,
    sample_trend_factory,
) -> None:
    target = date(2026, 7, 4)
    for index in range(4):
        cluster = await sample_cluster_factory(importance=float(100 - index))
        await sample_article_factory(
            cluster_id=cluster.id,
            published_at=datetime(2026, 7, 4, index, tzinfo=UTC),
        )
    old_cluster = await sample_cluster_factory(importance=999.0)
    await sample_article_factory(
        cluster_id=old_cluster.id,
        published_at=datetime(2026, 7, 3, 23, tzinfo=UTC),
    )
    for index in range(6):
        await sample_trend_factory(name=f"hot-{index}", growth_rate=float(10 - index))
    await sample_trend_factory(name="stable", growth_rate=100.0, status="stable")

    dashboard = await DashboardService(async_session).get_dashboard(target)

    assert dashboard.brief is None
    assert len(dashboard.top_clusters) == 3
    assert [cluster.importance for cluster in dashboard.top_clusters] == [
        100.0,
        99.0,
        98.0,
    ]
    assert len(dashboard.trend_highlights) == 5
    assert all(
        trend.status in {"exploding", "rising"} for trend in dashboard.trend_highlights
    )


@pytest.mark.asyncio
async def test_trend_service_paginates_with_real_total(
    async_session, sample_trend_factory
) -> None:
    for index in range(3):
        await sample_trend_factory(growth_rate=float(index))

    page = await TrendService(async_session).list_trends(page=2, page_size=2)

    assert page.total == 3
    assert len(page.items) == 1
