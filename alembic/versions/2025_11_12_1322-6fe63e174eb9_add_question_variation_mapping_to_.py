"""add_question_variation_mapping_to_company_trackers

Revision ID: 6fe63e174eb9
Revises: add_company_tracking_fc
Create Date: 2025-11-12 13:22:39.687339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fe63e174eb9'
down_revision: Union[str, None] = 'add_company_tracking_fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add question_variation_mapping JSON column to company_trackers table."""
    # Add the JSON column to store question variation mappings
    op.add_column('company_trackers',
        sa.Column('question_variation_mapping', sa.JSON(), nullable=True)
    )
    
    # Add comment for documentation
    op.execute("""
        COMMENT ON COLUMN company_trackers.question_variation_mapping IS 
        'JSON mapping of question IDs to variation IDs. Example: {"fc_q3": 123, "fc_q11": 456}. NULL or {} means use default questions.'
    """)


def downgrade() -> None:
    """Remove question_variation_mapping column from company_trackers table."""
    op.drop_column('company_trackers', 'question_variation_mapping')
