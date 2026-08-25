import asyncio
import os
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.core.config import get_settings

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres:postgres@localhost/aidevpulse'
os.environ['REDIS_URL'] = 'redis://localhost:6379'
os.environ['ENVIRONMENT'] = 'local'
os.environ['AICREDITS_API_KEY'] = 'dummy'
os.environ['AICREDITS_BASE_URL'] = 'https://api.aicredits.in/v1'
os.environ['AICREDITS_CHAT_MODEL'] = 'deepseek/deepseek-v3.2'
os.environ['AICREDITS_EMBEDDING_MODEL'] = 'text-embedding-3-small'

async def main():
    try:
        async with AsyncSessionLocal() as session:
            # Query 1: daily_briefs
            print("--- daily_briefs (last 7) ---")
            try:
                result = await session.execute(
                    text("SELECT date, stories_analyzed, stories_filtered, stories_selected FROM daily_briefs ORDER BY date DESC LIMIT 7")
                )
                for row in result:
                    print(row)
            except Exception as e:
                print(f"Error: {e}")

            # Query 2: story_clusters
            print("\n--- story_clusters (top 10 by importance) ---")
            try:
                result = await session.execute(
                    text("SELECT id, title, importance, action, created_at, updated_at FROM story_clusters ORDER BY importance DESC NULLS LAST LIMIT 10")
                )
                for row in result:
                    print(row)
            except Exception as e:
                print(f"Error: {e}")

            # Query 3: articles by source
            print("\n--- articles by source ---")
            try:
                result = await session.execute(
                    text("SELECT source, COUNT(*), MAX(published_at) as newest, MIN(published_at) as oldest FROM articles GROUP BY source")
                )
                for row in result:
                    print(row)
            except Exception as e:
                print(f"Error: {e}")

            # Query 4: papers count
            print("\n--- papers count ---")
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM papers"))
                print(result.scalar())
            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(main())
