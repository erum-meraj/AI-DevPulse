"""papers + paper_relevance_weights

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-10

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "papers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("arxiv_id", sa.Text(), nullable=False, unique=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("upvotes", sa.Integer(), nullable=True),
        sa.Column("github_stars", sa.Integer(), nullable=True),
        sa.Column("ai_keywords", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "paper_relevance_weights",
        sa.Column("keyword", sa.Text(), primary_key=True),
        sa.Column("weight", sa.Float(), nullable=False, server_default=sa.text("1.0")),
    )


def downgrade() -> None:
    op.drop_table("paper_relevance_weights")
    op.drop_table("papers")
