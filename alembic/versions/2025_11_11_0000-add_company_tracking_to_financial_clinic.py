"""add_company_tracking_to_financial_clinic

Revision ID: add_company_tracking_fc
Revises: 
Create Date: 2025-11-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_company_tracking_fc'
down_revision = '6593ad32fc2a'  # Current head
branch_labels = None
depends_on = None


def upgrade():
    """Add company_tracker_id to financial_clinic_responses table."""
    # Add company_tracker_id column
    op.add_column(
        'financial_clinic_responses',
        sa.Column('company_tracker_id', sa.Integer(), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_financial_clinic_responses_company_tracker_id',
        'financial_clinic_responses',
        'company_trackers',
        ['company_tracker_id'],
        ['id']
    )
    
    # Add index for better query performance
    op.create_index(
        'ix_financial_clinic_responses_company_tracker_id',
        'financial_clinic_responses',
        ['company_tracker_id']
    )


def downgrade():
    """Remove company_tracker_id from financial_clinic_responses table."""
    # Drop index
    op.drop_index('ix_financial_clinic_responses_company_tracker_id', table_name='financial_clinic_responses')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_financial_clinic_responses_company_tracker_id', 'financial_clinic_responses', type_='foreignkey')
    
    # Drop column
    op.drop_column('financial_clinic_responses', 'company_tracker_id')
