"""Add enable_company_field to company_trackers and ops admin role

Revision ID: add_enable_company_field_ops
Revises: 2026_01_06_1430_123456789abc
Create Date: 2026-01-07 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'add_enable_company_field_ops'
down_revision: Union[str, None] = '2026_01_06_1430_123456789abc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def table_exists(table_name):
    """Check if a table exists."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    # Add enable_company_field to company_trackers table
    # This controls whether the company/employer field is shown on the profile page for this Unique URL
    if table_exists('company_trackers') and not column_exists('company_trackers', 'enable_company_field'):
        op.add_column('company_trackers', 
            sa.Column('enable_company_field', sa.Boolean(), nullable=False, server_default='true')
        )
    
    # Note: The admin_role column already supports string values.
    # The "ops" role is handled at the application level - no schema change needed.
    # The current admin_role column is String(20) which can hold "full", "view_only", or "ops"


def downgrade() -> None:
    # Remove enable_company_field from company_trackers
    if table_exists('company_trackers') and column_exists('company_trackers', 'enable_company_field'):
        op.drop_column('company_trackers', 'enable_company_field')
