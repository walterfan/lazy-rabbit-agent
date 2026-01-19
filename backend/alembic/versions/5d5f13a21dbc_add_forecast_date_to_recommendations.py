"""add_forecast_date_to_recommendations

Revision ID: 5d5f13a21dbc
Revises: 1526ee29b8ab
Create Date: 2025-12-16 22:06:54.919912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d5f13a21dbc'
down_revision: Union[str, None] = '1526ee29b8ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add forecast_date column
    op.add_column('recommendations', sa.Column('forecast_date', sa.Date(), nullable=True))
    
    # Add index on (user_id, forecast_date, created_at DESC)
    op.create_index(
        'ix_recommendations_user_forecast_created',
        'recommendations',
        ['user_id', 'forecast_date', 'created_at'],
        unique=False
    )


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_recommendations_user_forecast_created', table_name='recommendations')
    
    # Drop column
    op.drop_column('recommendations', 'forecast_date')


