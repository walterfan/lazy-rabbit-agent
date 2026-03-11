"""Add llm_settings table for per-user LLM configuration.

Revision ID: 010
Create Date: 2026-03-10
"""

from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "llm_settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False, unique=True, index=True),
        # Text generation
        sa.Column("chat_base_url", sa.String(500), nullable=True),
        sa.Column("chat_api_key", sa.Text(), nullable=True),
        sa.Column("chat_model", sa.String(255), nullable=True),
        sa.Column("chat_temperature", sa.Float(), nullable=True),
        # Embedding
        sa.Column("embedding_base_url", sa.String(500), nullable=True),
        sa.Column("embedding_api_key", sa.Text(), nullable=True),
        sa.Column("embedding_model", sa.String(255), nullable=True),
        # Image generation
        sa.Column("image_base_url", sa.String(500), nullable=True),
        sa.Column("image_api_key", sa.Text(), nullable=True),
        sa.Column("image_model", sa.String(255), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("llm_settings")
