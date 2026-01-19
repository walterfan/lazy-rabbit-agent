"""add_user_roles

Revision ID: f652314fb150
Revises: daa091af06f2
Create Date: 2025-12-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f652314fb150'
down_revision: Union[str, None] = 'daa091af06f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM type for PostgreSQL
    user_role = sa.Enum('super_admin', 'admin', 'user', 'guest', name='userrole')
    user_role.create(op.get_bind(), checkfirst=True)
    
    # Add role column with default 'user'
    op.add_column('users', 
        sa.Column('role', 
            user_role,
            nullable=False,
            server_default='user'
        )
    )
    
    # Set first user (lowest id) as super_admin
    op.execute("""
        UPDATE users 
        SET role = 'super_admin' 
        WHERE id = (SELECT MIN(id) FROM users)
    """)
    
    # Create index for role column
    op.create_index('ix_users_role', 'users', ['role'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_users_role', table_name='users')
    
    # Drop role column
    op.drop_column('users', 'role')
    
    # Drop ENUM type for PostgreSQL
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
