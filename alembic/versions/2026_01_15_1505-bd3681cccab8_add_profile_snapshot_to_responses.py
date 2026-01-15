"""add_profile_snapshot_to_responses

Revision ID: bd3681cccab8
Revises: 51859804e36c
Create Date: 2026-01-15 15:05:04.171370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd3681cccab8'
down_revision: Union[str, None] = '51859804e36c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add profile_snapshot column to financial_clinic_responses
    op.add_column('financial_clinic_responses', 
                  sa.Column('profile_snapshot', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove profile_snapshot column
    op.drop_column('financial_clinic_responses', 'profile_snapshot')
