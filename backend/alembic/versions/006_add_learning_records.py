"""Add learning_records table for Personal Secretary agent

Revision ID: 006
Revises: 005
Create Date: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create learning record type enum
    learning_record_type_enum = postgresql.ENUM(
        'word', 'sentence', 'topic', 'article', 'question', 'idea',
        name='learningrecordtype',
        create_type=True
    )
    learning_record_type_enum.create(op.get_bind(), checkfirst=True)

    # Create learning_records table
    op.create_table(
        'learning_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column(
            'input_type',
            sa.Enum(
                'word', 'sentence', 'topic', 'article', 'question', 'idea',
                name='learningrecordtype'
            ),
            nullable=False
        ),
        sa.Column('user_input', sa.Text(), nullable=False),
        sa.Column('response_payload', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('review_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_records_id'), 'learning_records', ['id'], unique=False)
    op.create_index(op.f('ix_learning_records_user_id'), 'learning_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_learning_records_input_type'), 'learning_records', ['input_type'], unique=False)
    
    # Create index for searching (user_input text search)
    # Note: Full-text search index depends on database; this is basic
    op.create_index(
        'ix_learning_records_user_input',
        'learning_records',
        ['user_input'],
        unique=False,
        postgresql_using='btree'
    )


def downgrade() -> None:
    op.drop_index('ix_learning_records_user_input', table_name='learning_records')
    op.drop_index(op.f('ix_learning_records_input_type'), table_name='learning_records')
    op.drop_index(op.f('ix_learning_records_user_id'), table_name='learning_records')
    op.drop_index(op.f('ix_learning_records_id'), table_name='learning_records')
    op.drop_table('learning_records')
    
    # Drop enum type
    learning_record_type_enum = postgresql.ENUM(
        'word', 'sentence', 'topic', 'article', 'question', 'idea',
        name='learningrecordtype'
    )
    learning_record_type_enum.drop(op.get_bind(), checkfirst=True)
