"""Add medical paper tables.

Revision ID: 008
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "medical_paper_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("paper_type", sa.String(20), nullable=False, server_default="rct"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending", index=True),
        sa.Column("research_question", sa.Text(), nullable=False),
        sa.Column("study_design", sa.JSON(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.Column("manuscript", sa.JSON(), nullable=True),
        sa.Column("references", sa.JSON(), nullable=True),
        sa.Column("stats_report", sa.JSON(), nullable=True),
        sa.Column("compliance_report", sa.JSON(), nullable=True),
        sa.Column("current_step", sa.String(50), nullable=True),
        sa.Column("revision_round", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "paper_task_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("task_id", sa.String(36), sa.ForeignKey("medical_paper_tasks.id"), nullable=False, index=True),
        sa.Column("sender", sa.String(50), nullable=False),
        sa.Column("receiver", sa.String(50), nullable=False),
        sa.Column("intent", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=True),
        sa.Column("output_payload", sa.JSON(), nullable=True),
        sa.Column("error", sa.JSON(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("tokens_in", sa.Integer(), nullable=True),
        sa.Column("tokens_out", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("paper_task_messages")
    op.drop_table("medical_paper_tasks")
