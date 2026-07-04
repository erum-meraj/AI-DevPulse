from apscheduler.schedulers.background import BackgroundScheduler

from app.tasks.celery_app import build_scheduler, celery_app
from app.tasks.embedding_tasks import generate_embeddings
from app.tasks.ingestion_tasks import collect_articles


def test_collect_articles_task_is_registered() -> None:
    assert collect_articles.name == "app.tasks.ingestion_tasks.collect_articles"
    assert collect_articles.name in celery_app.tasks


def test_collect_articles_scheduler_registration() -> None:
    scheduler = build_scheduler()
    collect_job = scheduler.get_job("collect_articles_every_30_minutes")
    embedding_job = scheduler.get_job("generate_embeddings_every_10_minutes")

    assert isinstance(scheduler, BackgroundScheduler)
    assert collect_job is not None
    assert embedding_job is not None
    assert collect_job.trigger.interval.total_seconds() == 1800
    assert embedding_job.trigger.interval.total_seconds() == 600


def test_generate_embeddings_task_is_registered() -> None:
    assert generate_embeddings.name == "app.tasks.embedding_tasks.generate_embeddings"
    assert generate_embeddings.name in celery_app.tasks
