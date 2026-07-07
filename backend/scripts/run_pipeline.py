import asyncio
from backend.app.db import model_registry
from backend.app.db.session import AsyncSessionLocal
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.clustering_service import ClusteringService
from backend.app.services.analysis_service import AnalysisService
from backend.app.services.ranking_service import RankingService
from backend.app.repositories.cluster_repo import ClusterRepository
from backend.app.repositories.article_repo import ArticleRepository


async def run_pipeline():
    async with AsyncSessionLocal() as session:
        print("=" * 50)
        print("STAGE 1: Embedding")
        print("=" * 50)
        embedding_service = EmbeddingService(session)
        embed_result = await embedding_service.embed_pending_articles(limit=50)
        print(f"Embedding result: {embed_result}")
        await session.commit()

        print()
        print("=" * 50)
        print("STAGE 2: Clustering")
        print("=" * 50)
        clustering_service = ClusteringService(session)
        cluster_result = await clustering_service.cluster_pending_articles(limit=50)
        print(f"Clustering result: {cluster_result}")
        await session.commit()

        print()
        print("=" * 50)
        print("STAGE 3: Analysis + Ranking (per cluster)")
        print("=" * 50)
        cluster_repo = ClusterRepository(session)
        article_repo = ArticleRepository(session)
        analysis_service = AnalysisService(session)
        ranking_service = RankingService(session)

        # Get all clusters updated recently (should include everything just created)
        clusters = await cluster_repo.get_recently_updated(within_days=1)
        print(f"Found {len(clusters)} clusters to analyze")

        for cluster in clusters:
            members = await article_repo.list_by_cluster_id(cluster.id)
            if not members:
                print(f"  Skipping cluster {cluster.id} (no members found)")
                continue
            print(
                f"  Analyzing cluster: {cluster.title[:60]} ({len(members)} articles)"
            )
            analysis = await analysis_service.analyze_cluster(cluster, members)
            await session.commit()
            print(
                f"    -> confidence={analysis.confidence}, sentiment={analysis.sentiment}"
            )

            importance = await ranking_service.rank_cluster(cluster)
            await session.commit()
            print(f"    -> importance={importance:.1f}, action={cluster.action}")

        print()
        print("=" * 50)
        print("PIPELINE COMPLETE")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run_pipeline())
