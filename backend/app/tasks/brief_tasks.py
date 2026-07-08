import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db import model_registry  # noqa: F401
from app.db.session import task_scoped_session
from app.services.daily_brief_service import DailyBriefService
from app.services.notification_service import NotificationService
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.brief_tasks.generate_daily_brief")
def generate_daily_brief() -> str:
    return asyncio.run(_generate_daily_brief())


async def _generate_daily_brief() -> str:
    settings = get_settings()
    today = datetime.now(ZoneInfo(settings.TIMEZONE)).date()
    async with task_scoped_session() as session:
        brief = await DailyBriefService(session).generate_for_date(today)
        await session.commit()
    NotificationService().send_daily_brief_email(brief)
    logger.info("generate_daily_brief_completed", date=str(today))
    return str(today)
