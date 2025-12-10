"""add_variation_control_flags

Revision ID: 51e7d91adcdc
Revises: 12b5be243f89
Create Date: 2025-12-10 22:04:14.707855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51e7d91adcdc'
down_revision: Union[str, None] = '12b5be243f89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add variation control flags to company_trackers table
    op.add_column('company_trackers', sa.Column('enable_variations', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('company_trackers', sa.Column('variations_enabled_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('company_trackers', sa.Column('variations_enabled_by', sa.Integer(), nullable=True))
    
    # Create index for enable_variations
    op.create_index('ix_company_trackers_enable_variations', 'company_trackers', ['enable_variations'])
    
    # Add foreign key constraint for variations_enabled_by
    op.create_foreign_key('fk_company_trackers_variations_enabled_by', 'company_trackers', 'users', ['variations_enabled_by'], ['id'])


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint('fk_company_trackers_variations_enabled_by', 'company_trackers', type_='foreignkey')
    
    # Remove index
    op.drop_index('ix_company_trackers_enable_variations', 'company_trackers')
    
    # Remove columns
    op.drop_column('company_trackers', 'variations_enabled_by')
    op.drop_column('company_trackers', 'variations_enabled_at')
    op.drop_column('company_trackers', 'enable_variations')
