"""Add cities table

Revision ID: 002
Revises: 001
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create cities table with indexes."""
    op.create_table(
        'cities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('location_id', sa.String(length=20), nullable=False),
        sa.Column('location_name_zh', sa.String(length=100), nullable=False),
        sa.Column('location_name_en', sa.String(length=100), nullable=True),
        sa.Column('ad_code', sa.String(length=10), nullable=False),
        sa.Column('province_zh', sa.String(length=50), nullable=True),
        sa.Column('province_en', sa.String(length=50), nullable=True),
        sa.Column('city_zh', sa.String(length=50), nullable=True),
        sa.Column('city_en', sa.String(length=50), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('location_id'),
        sa.UniqueConstraint('ad_code')
    )
    
    # Create indexes for fast lookups
    op.create_index(op.f('ix_cities_id'), 'cities', ['id'], unique=False)
    op.create_index(op.f('ix_cities_location_id'), 'cities', ['location_id'], unique=True)
    op.create_index(op.f('ix_cities_location_name_zh'), 'cities', ['location_name_zh'], unique=False)
    op.create_index(op.f('ix_cities_ad_code'), 'cities', ['ad_code'], unique=True)


def downgrade() -> None:
    """Drop cities table and indexes."""
    op.drop_index(op.f('ix_cities_ad_code'), table_name='cities')
    op.drop_index(op.f('ix_cities_location_name_zh'), table_name='cities')
    op.drop_index(op.f('ix_cities_location_id'), table_name='cities')
    op.drop_index(op.f('ix_cities_id'), table_name='cities')
    op.drop_table('cities')

