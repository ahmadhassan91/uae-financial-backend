"""add_admin_role_to_users

Revision ID: 12b5be243f89
Revises: add_scheduled_emails
Create Date: 2025-12-05 15:07:23.930788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12b5be243f89'
down_revision: Union[str, None] = 'add_scheduled_emails'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add admin_role column to users table
    op.add_column('users', sa.Column('admin_role', sa.String(20), nullable=False, server_default='full'))


def downgrade() -> None:
    # Remove admin_role column from users table
    op.drop_column('users', 'admin_role')
