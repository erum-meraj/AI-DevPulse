from datetime import UTC, date, datetime, timedelta
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_db
from app.main import create_app


@pytest_asyncio.fixture
async def client(async_session):
    """Uses httpx.AsyncClient with ASGITransport instead of Starlette's
    TestClient, because TestClient runs the app in a separate thread with
    its own event loop (via anyio's blocking portal), which breaks asyncpg
    connections bound to the test's own loop. ASGITransport runs the app
    in-process on the same loop as the test, so the shared async_session
    works correctly.
    """
    app = create_app()

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
@patch("app.api.v1.dashboard.current_local_date", return_value=date(2026, 7, 4))
async def test_api_routes_smoke(
    mock_current_date,
    client,
    async_session,
    sample_cluster_factory,
    sample_article_factory,
    sample_trend_factory,
    sample_daily_brief_factory,
) -> None:
    target_date = date(2026, 7, 4)

    cluster = await sample_cluster_factory(title="Agent tooling", importance=92.0)
    await sample_article_factory(
        cluster_id=cluster.id,
        published_at=datetime(2026, 7, 4, 10, tzinfo=UTC),
    )

    await sample_daily_brief_factory(
        date=target_date,
        summary="A strong brief for the day.",
        stories_analyzed=5,
        stories_filtered=2,
        stories_selected=3,
        estimated_read_time_minutes=3,
    )
    await sample_daily_brief_factory(
        date=target_date - timedelta(days=1),
        summary="Earlier brief.",
        stories_analyzed=3,
        stories_filtered=1,
        stories_selected=2,
        estimated_read_time_minutes=2,
    )
    await sample_daily_brief_factory(
        date=target_date - timedelta(days=2),
        summary="Old brief.",
        stories_analyzed=4,
        stories_filtered=1,
        stories_selected=3,
        estimated_read_time_minutes=4,
    )

    await sample_trend_factory(name="agents", growth_rate=3.2, status="exploding")
    await sample_trend_factory(name="benchmarks", growth_rate=1.5, status="rising")

    dashboard_response = await client.get("/api/v1/dashboard")
    assert dashboard_response.status_code == 200
    dashboard_payload = dashboard_response.json()
    assert dashboard_payload["brief"]["date"] == target_date.isoformat()
    assert len(dashboard_payload["top_clusters"]) >= 1
    assert len(dashboard_payload["trend_highlights"]) >= 1

    stories_response = await client.get("/api/v1/stories?page=1&page_size=2")
    assert stories_response.status_code == 200
    stories_payload = stories_response.json()
    assert stories_payload["page"] == 1
    assert stories_payload["page_size"] == 2
    assert len(stories_payload["items"]) >= 1

    story_response = await client.get(f"/api/v1/stories/{cluster.id}")
    assert story_response.status_code == 200
    story_payload = story_response.json()
    assert story_payload["id"] == str(cluster.id)
    assert len(story_payload["member_articles"]) >= 1

    clusters_response = await client.get("/api/v1/clusters?page=1&page_size=2")
    assert clusters_response.status_code == 200
    clusters_payload = clusters_response.json()
    assert clusters_payload["items"]

    trends_response = await client.get("/api/v1/trends?page=1&page_size=2")
    assert trends_response.status_code == 200
    trends_payload = trends_response.json()
    assert trends_payload["page"] == 1
    assert trends_payload["page_size"] == 2

    brief_response = await client.get(f"/api/v1/daily-brief?date={target_date.isoformat()}")
    assert brief_response.status_code == 200
    brief_payload = brief_response.json()
    assert brief_payload["date"] == target_date.isoformat()

    weekly_response = await client.get("/api/v1/weekly-report")
    assert weekly_response.status_code == 200
    weekly_payload = weekly_response.json()
    assert len(weekly_payload["briefs"]) == 3
    assert weekly_payload["totals"]["stories_analyzed"] == 12
    assert weekly_payload["totals"]["avg_read_time_minutes"] == 3.0

    missing_story_response = await client.get(
        "/api/v1/stories/00000000-0000-0000-0000-000000000000"
    )
    assert missing_story_response.status_code == 404
    assert missing_story_response.json()["error"]["code"] == "not_found"

    docs_response = await client.get("/docs")
    assert docs_response.status_code == 200
    assert "swagger" in docs_response.text.lower()
