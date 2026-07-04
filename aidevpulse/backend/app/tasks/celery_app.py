from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "aidevpulse",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.update(
    timezone=settings.TIMEZONE,
    task_default_queue="aidevpulse",
)

_scheduler: BackgroundScheduler | None = None


def trigger_collect_articles() -> None:
    from app.tasks.ingestion_tasks import collect_articles

    collect_articles.delay()


def trigger_generate_embeddings() -> None:
    from app.tasks.embedding_tasks import generate_embeddings

    generate_embeddings.delay()


def register_scheduler_jobs(scheduler: BackgroundScheduler) -> None:
    scheduler.add_job(
        trigger_collect_articles,
        IntervalTrigger(minutes=30, timezone=settings.TIMEZONE),
        id="collect_articles_every_30_minutes",
        replace_existing=True,
    )
    scheduler.add_job(
        trigger_generate_embeddings,
        IntervalTrigger(minutes=10, timezone=settings.TIMEZONE),
        id="generate_embeddings_every_10_minutes",
        replace_existing=True,
    )


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=settings.TIMEZONE)
    register_scheduler_jobs(scheduler)
    return scheduler


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = build_scheduler()
        _scheduler.start()
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
