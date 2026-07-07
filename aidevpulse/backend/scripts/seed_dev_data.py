#!/usr/bin/env python3
"""
Development-only seed script.

WARNING: This script is for development use ONLY. It deletes all existing data
in the target tables before inserting new sample data. Do not run in production.
"""

import asyncio
import os
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

# Add the app directory to the path for imports
app_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(app_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

# Load environment variables from .env file
env_path = app_dir / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

from app.core.config import get_settings
from app.models.daily_brief import DailyBrief
from app.models.trend import Trend
from app.repositories.article_repo import ArticleRepository
from app.repositories.cluster_repo import ClusterRepository
from app.repositories.daily_brief_repo import DailyBriefRepository
from app.repositories.trend_repo import TrendRepository
from app.services.action_service import recommend_action


def current_local_date() -> date:
    """Get the current local date as a date object."""
    from zoneinfo import ZoneInfo

    settings = get_settings()
    return datetime.now(ZoneInfo(settings.TIMEZONE)).date()


async def seed_data():
    """Main seed function that inserts sample data."""
    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not set")
        return

    # Create async engine and session
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Initialize repositories
        daily_brief_repo = DailyBriefRepository(session)
        cluster_repo = ClusterRepository(session)
        article_repo = ArticleRepository(session)
        trend_repo = TrendRepository(session)

        today = current_local_date()

        # ============================================================================
        # STEP 1: Delete existing data (dev-only, NOT for production!)
        # ============================================================================
        print(f"[*] Clearing existing data for date: {today}")

        # Delete trends
        trends_result = await session.execute(select(Trend))
        trends = trends_result.scalars().all()
        for trend in trends:
            await session.delete(trend)
        await session.flush()

        # Delete articles (foreign key constraint to clusters)
        from app.models.cluster import StoryCluster
        from app.models.article import Article

        articles_result = await session.execute(select(Article))
        articles = articles_result.scalars().all()
        for article in articles:
            await session.delete(article)
        await session.flush()

        # Delete clusters
        clusters_result = await session.execute(select(StoryCluster))
        clusters = clusters_result.scalars().all()
        for cluster in clusters:
            await session.delete(cluster)
        await session.flush()

        # Delete daily briefs
        daily_briefs_result = await session.execute(select(DailyBrief))
        daily_briefs = daily_briefs_result.scalars().all()
        for daily_brief in daily_briefs:
            await session.delete(daily_brief)
        await session.flush()

        print("[+] Existing data cleared")

        # ============================================================================
        # STEP 2: Insert DailyBrief for today
        # ============================================================================
        print("[*] Inserting DailyBrief")

        daily_brief = await daily_brief_repo.create(
            date=today,
            summary="Today's major AI engineering developments include browser agent releases, extended reasoning models, and MCP protocol adoption.",
            stories_analyzed=146,
            stories_filtered=138,
            stories_selected=8,
            estimated_read_time_minutes=9,
        )
        await session.flush()
        print(f"[+] DailyBrief inserted with ID: {daily_brief.id}")

        # ============================================================================
        # STEP 3: Insert 8 StoryCluster rows
        # ============================================================================
        print("[*] Inserting StoryClusters")

        # Cluster data with realistic values
        cluster_data = [
            {
                "title": "OpenAI launches Browser Agent API",
                "cluster_summary": "OpenAI introduces a new Browser Agent API that allows developers to build AI agents capable of interacting directly with web browsers for automated tasks and information retrieval.",
                "why_it_matters": "This enables more autonomous AI systems that can navigate websites, extract data, and perform actions without manual intervention.",
                "importance": 97,
                "confidence": "very_high",
                "sentiment": "positive",
                "discussion_count": 2500,
            },
            {
                "title": "Anthropic releases Claude 3.7 with Extended Thinking",
                "cluster_summary": "Anthropic announces Claude 3.7 featuring 'Extended Thinking' mode that allows the model to reason through complex problems with longer chain-of-thought processing.",
                "why_it_matters": "Extended Thinking significantly improves Claude's ability to solve math problems, code challenges, and multi-step reasoning tasks.",
                "importance": 95,
                "confidence": "very_high",
                "sentiment": "positive",
                "discussion_count": 1800,
            },
            {
                "title": "Model Context Protocol hits 10,000 integrations",
                "cluster_summary": "The Model Context Protocol (MCP) has reached a milestone of 10,000 integrated applications, demonstrating rapid adoption across the AI ecosystem.",
                "why_it_matters": "MCP provides a standardized way for applications to share context with AI models, enabling more capable and context-aware AI assistants.",
                "importance": 92,
                "confidence": "high",
                "sentiment": "positive",
                "discussion_count": 1200,
            },
            {
                "title": "GitHub Copilot adds multi-file agent mode in VS Code",
                "cluster_summary": "GitHub Copilot introduces a new multi-file agent mode in VS Code that can understand and modify code across multiple files in a project.",
                "why_it_matters": "This represents a significant step toward true AI pair programming that can handle complex refactoring and project-wide changes.",
                "importance": 90,
                "confidence": "high",
                "sentiment": "positive",
                "discussion_count": 950,
            },
            {
                "title": "HuggingFace SmolLM3 outperforms 7B models at 3B params",
                "cluster_summary": "HuggingFace releases SmolLM3, a 3B parameter model that outperforms existing 7B models on standard benchmarks while being significantly faster and cheaper to run.",
                "why_it_matters": "This continues the trend of model efficiency improvements, making powerful AI more accessible for edge devices and low-resource environments.",
                "importance": 88,
                "confidence": "high",
                "sentiment": "positive",
                "discussion_count": 780,
            },
            {
                "title": "LangChain releases LangGraph v0.3 with persistent memory",
                "cluster_summary": "LangChain introduces LangGraph v0.3 featuring persistent memory capabilities that allow AI agents to maintain state across multiple interactions.",
                "why_it_matters": "Persistent memory enables more coherent multi-turn conversations and allows agents to remember important context over time.",
                "importance": 85,
                "confidence": "medium",
                "sentiment": "positive",
                "discussion_count": 520,
            },
            {
                "title": "Meta open-sources Llama 3.2 multimodal 11B",
                "cluster_summary": "Meta releases Llama 3.2, including an 11B multimodal model that can process both text and images, competing with proprietary multimodal models.",
                "why_it_matters": "Open-source multimodal models democratize access to advanced AI capabilities and reduce reliance on proprietary APIs.",
                "importance": 82,
                "confidence": "medium",
                "sentiment": "positive",
                "discussion_count": 2100,
            },
            {
                "title": "DeepMind publishes analysis of agent planning failures",
                "cluster_summary": "DeepMind releases a comprehensive analysis of common failure modes in AI agent planning systems and proposes strategies for mitigating them.",
                "why_it_matters": "Understanding and addressing planning failures is crucial for deploying safe and reliable AI agents in production environments.",
                "importance": 74,
                "confidence": "medium",
                "sentiment": "neutral",
                "discussion_count": 340,
            },
        ]

        # Define hours ago for each article
        hours_ago = [2, 5, 6, 8, 10, 11, 12, 14]

        # Cycle through sources
        sources = ["openai", "anthropic", "hackernews", "huggingface"]

        clusters = []
        for i, data in enumerate(cluster_data):
            # Determine action based on importance
            action = recommend_action(data["importance"])

            # Create cluster
            cluster = await cluster_repo.create(
                title=data["title"],
                cluster_summary=data["cluster_summary"],
                why_it_matters=data["why_it_matters"],
                importance=data["importance"],
                confidence=data["confidence"],
                sentiment=data["sentiment"],
                discussion_count=data["discussion_count"],
                action=action,
            )
            await session.flush()
            clusters.append(cluster)
            print(
                f"[+] Cluster {i + 1} inserted: {cluster.title} (importance: {cluster.importance}, action: {cluster.action})"
            )

            # Create corresponding article
            hours = hours_ago[i]
            source = sources[i % len(sources)]
            published_at = datetime.now(UTC) - timedelta(hours=hours)

            article = await article_repo.create(
                title=f"{data['title']} - Detailed Coverage",
                content=f"Full article content about {data['title']} including technical details, use cases, and community response.",
                url=f"https://example.com/articles/{today.strftime('%Y%m%d')}_{i + 1}",
                source=source,
                external_id=f"article-{today.strftime('%Y%m%d')}-{i + 1}",
                published_at=published_at,
                status="ranked",
                importance=cluster.importance,
                confidence=cluster.confidence,
                cluster_id=cluster.id,
            )
            await session.flush()
            print(
                f"[+] Article {i + 1} inserted (published {hours}h ago, source: {article.source})"
            )

        # ============================================================================
        # STEP 4: Insert 4 Trend rows
        # ============================================================================
        print("[*] Inserting Trends")

        trend_data = [
            {"name": "Browser Agents", "growth_rate": 2.5, "status": "exploding"},
            {"name": "MCP Protocol", "growth_rate": 0.8, "status": "rising"},
            {"name": "Tool Use", "growth_rate": 0.6, "status": "rising"},
            {"name": "Multimodal Hype", "growth_rate": -0.4, "status": "declining"},
        ]

        for data in trend_data:
            trend = await trend_repo.create(
                name=data["name"],
                mentions_today=None,
                mentions_7d_avg=None,
                growth_rate=data["growth_rate"],
                status=data["status"],
            )
            await session.flush()
            print(
                f"[+] Trend inserted: {trend.name} (growth_rate: {trend.growth_rate}, status: {trend.status})"
            )

        await session.commit()

        # ============================================================================
        # SUMMARY
        # ============================================================================
        print("\n" + "=" * 50)
        print("SEEDING COMPLETE")
        print("=" * 50)
        print(f"DailyBriefs: 1")
        print(f"StoryClusters: {len(clusters)}")
        print(f"Articles: {len(clusters)}")
        print(f"Trends: {len(trend_data)}")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(seed_data())
