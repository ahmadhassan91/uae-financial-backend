"""add_completed_at_to_financial_clinic_responses

Revision ID: 75eceb034b5b
Revises: b52a1a5a8503
Create Date: 2025-11-18 01:19:38.259877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75eceb034b5b'
down_revision: Union[str, None] = 'b52a1a5a8503'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add completed_at column to financial_clinic_responses table
    op.add_column('financial_clinic_responses', 
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove completed_at column from financial_clinic_responses table
    op.drop_column('financial_clinic_responses', 'completed_at')
