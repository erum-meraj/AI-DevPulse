import asyncio

from app.core.logging import get_logger
from app.db import model_registry  # noqa: F401
from app.db.session import task_scoped_session
from app.connectors.huggingface_papers import HuggingFacePapersConnector
from app.repositories.paper_repo import PaperRepository
from app.services.paper_scoring_service import PaperScoringService
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.paper_tasks.collect_papers")
def collect_papers() -> dict[str, int]:
    return asyncio.run(_collect_papers())


async def _collect_papers() -> dict[str, int]:
    connector = HuggingFacePapersConnector()
    raw_papers = await connector.fetch_papers()

    created = 0
    skipped = 0

    async with task_scoped_session() as session:
        paper_repo = PaperRepository(session)
        scoring_service = PaperScoringService(session)
        weights = await scoring_service.weight_repo.get_all_weights()

        for raw in raw_papers:
            if not raw["arxiv_id"]:
                skipped += 1
                continue
            existing = await paper_repo.get_by_arxiv_id(raw["arxiv_id"])
            if existing is not None:
                skipped += 1
                continue

            paper = await paper_repo.create(**raw)
            score = await scoring_service.score_paper(paper, weights=weights)
            paper.relevance_score = score
            created += 1

        await session.commit()

    logger.info("collect_papers_completed", created=created, skipped=skipped)
    return {"created": created, "skipped": skipped}
