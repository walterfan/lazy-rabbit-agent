"""add_send_type_to_email_logs

Revision ID: 0110d4d0da9b
Revises: 5d5f13a21dbc
Create Date: 2025-12-18 22:02:19.710446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0110d4d0da9b'
down_revision: Union[str, None] = '5d5f13a21dbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add send_type column to email_logs table
    op.add_column('email_logs', sa.Column('send_type', sa.String(length=20), nullable=True))
    
    # Create index on send_type for query performance
    op.create_index('ix_email_logs_send_type', 'email_logs', ['send_type'], unique=False)


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_email_logs_send_type', table_name='email_logs')
    
    # Remove send_type column
    op.drop_column('email_logs', 'send_type')


