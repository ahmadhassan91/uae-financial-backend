"""add_survey_response_id_to_consultation_requests

Revision ID: 1a05d3369003
Revises: bd3681cccab8
Create Date: 2026-01-15 18:35:33.950485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a05d3369003'
down_revision: Union[str, None] = 'bd3681cccab8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('consultation_requests', 
        sa.Column('survey_response_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_consultation_requests_survey_response_id',
        'consultation_requests', 
        'financial_clinic_responses',
        ['survey_response_id'], 
        ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_consultation_requests_survey_response_id', 'consultation_requests', type_='foreignkey')
    op.drop_column('consultation_requests', 'survey_response_id')
