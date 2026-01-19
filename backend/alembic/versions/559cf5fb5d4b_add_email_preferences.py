"""add_email_preferences

Revision ID: 559cf5fb5d4b
Revises: 004
Create Date: 2025-12-15 21:52:02.175596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '559cf5fb5d4b'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add email notification preference fields to users table
    op.add_column('users', sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('email_send_time', sa.Time(), nullable=True))
    op.add_column('users', sa.Column('email_additional_recipients', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('email_preferred_city', sa.String(length=20), nullable=True))


def downgrade() -> None:
    # Remove email notification preference fields from users table
    op.drop_column('users', 'email_preferred_city')
    op.drop_column('users', 'email_additional_recipients')
    op.drop_column('users', 'email_send_time')
    op.drop_column('users', 'email_notifications_enabled')


