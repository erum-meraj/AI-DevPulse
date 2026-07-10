"""One-off script: seeds paper_relevance_weights from existing topics.name
values, plus a small set of AI-research-specific defaults not likely to
already exist as article topics. Run manually once:
python -m scripts.seed_paper_weights
Safe to re-run -- uses set_weight (upsert), won't duplicate or error on
existing keywords. Remember: this is a standalone script, so per bug #8
in the status doc, an explicit session.commit() at the end is required or
the whole transaction silently rolls back."""

import asyncio

from app.db import model_registry  # noqa: F401
from app.db.session import AsyncSessionLocal
from app.repositories.paper_repo import PaperRelevanceWeightRepository
from app.repositories.topic_repo import TopicRepository

DEFAULT_RESEARCH_KEYWORDS = {
    "reinforcement learning": 1.2,
    "diffusion models": 1.0,
    "large language models": 1.5,
    "agents": 1.5,
    "multimodal": 1.0,
    "reasoning": 1.3,
    "fine-tuning": 1.0,
    "benchmark": 0.8,
}


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        weight_repo = PaperRelevanceWeightRepository(session)
        topic_repo = TopicRepository(session)

        topics = await topic_repo.list_all()
        seeded = 0
        for topic in topics:
            await weight_repo.set_weight(topic.name.lower(), 1.0)
            seeded += 1

        for keyword, weight in DEFAULT_RESEARCH_KEYWORDS.items():
            await weight_repo.set_weight(keyword, weight)
            seeded += 1

        await session.commit()
        print(f"Seeded {seeded} relevance weight rows (some may be updates to existing rows).")


if __name__ == "__main__":
    asyncio.run(seed())
