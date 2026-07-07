"""initial schema: extensions + articles, story_clusters, topics, article_topics,
daily_briefs, trends

Revision ID: 0001
Revises:
Create Date: 2026-07-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

EMBEDDING_DIMENSIONS = 1536


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')

    op.create_table(
        "story_clusters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("cluster_summary", sa.Text(), nullable=True),
        sa.Column("why_it_matters", sa.Text(), nullable=True),
        sa.Column("importance", sa.Float(), nullable=True),
        sa.Column("confidence", sa.VARCHAR(length=20), nullable=True),
        sa.Column("sentiment", sa.VARCHAR(length=20), nullable=True),
        sa.Column("discussion_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("action", sa.VARCHAR(length=20), nullable=True),
        sa.Column("centroid_embedding", Vector(EMBEDDING_DIMENSIONS), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False, unique=True),
        sa.Column("source", sa.VARCHAR(length=50), nullable=False),
        sa.Column("external_id", sa.Text(), nullable=True),
        sa.Column("author", sa.Text(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("comment_count", sa.Integer(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSIONS), nullable=True),
        sa.Column("cluster_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("story_clusters.id", ondelete="SET NULL"), nullable=True),
        sa.Column("importance", sa.Float(), nullable=True),
        sa.Column("confidence", sa.VARCHAR(length=20), nullable=True),
        sa.Column("status", sa.VARCHAR(length=20), nullable=False, server_default=sa.text("'pending'")),
    )
    op.create_index("ix_articles_source_external_id", "articles", ["source", "external_id"])
    op.create_index("ix_articles_cluster_id", "articles", ["cluster_id"])
    op.create_index("ix_articles_published_at", "articles", ["published_at"])
    op.execute(
        "CREATE INDEX ix_articles_embedding_hnsw ON articles "
        "USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute(
        "CREATE INDEX ix_story_clusters_centroid_hnsw ON story_clusters "
        "USING hnsw (centroid_embedding vector_cosine_ops)"
    )

    op.create_table(
        "topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "article_topics",
        sa.Column("article_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "daily_briefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("date", sa.Date(), nullable=False, unique=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("estimated_read_time_minutes", sa.Integer(), nullable=True),
        sa.Column("stories_analyzed", sa.Integer(), nullable=True),
        sa.Column("stories_filtered", sa.Integer(), nullable=True),
        sa.Column("stories_selected", sa.Integer(), nullable=True),
        sa.Column("top_cluster_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "trends",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("mentions_today", sa.Integer(), nullable=True),
        sa.Column("mentions_7d_avg", sa.Float(), nullable=True),
        sa.Column("growth_rate", sa.Float(), nullable=True),
        sa.Column("status", sa.VARCHAR(length=20), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Referenced by Discord /bookmark command (spec §15) — no table existed for it in v1.


def downgrade() -> None:
    op.drop_table("trends")
    op.drop_table("daily_briefs")
    op.drop_table("article_topics")
    op.drop_table("topics")
    op.execute("DROP INDEX IF EXISTS ix_story_clusters_centroid_hnsw")
    op.execute("DROP INDEX IF EXISTS ix_articles_embedding_hnsw")
    op.drop_index("ix_articles_published_at", table_name="articles")
    op.drop_index("ix_articles_cluster_id", table_name="articles")
    op.drop_index("ix_articles_source_external_id", table_name="articles")
    op.drop_table("articles")
    op.drop_table("story_clusters")
