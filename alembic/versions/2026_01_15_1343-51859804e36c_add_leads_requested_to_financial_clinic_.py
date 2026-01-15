"""add_leads_requested_to_financial_clinic_responses

Revision ID: 51859804e36c
Revises: d579303e1733
Create Date: 2026-01-15 13:43:38.209162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51859804e36c'
down_revision: Union[str, None] = 'd579303e1733'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add leads_requested column to financial_clinic_responses table
    op.add_column('financial_clinic_responses', 
                  sa.Column('leads_requested', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove leads_requested column from financial_clinic_responses table
    op.drop_column('financial_clinic_responses', 'leads_requested')
