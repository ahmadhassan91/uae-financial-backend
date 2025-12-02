"""add_financial_clinic_fields_and_products

Revision ID: 001b495bba1c
Revises: c483380ec75e
Create Date: 2025-10-15 23:58:42.163938

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001b495bba1c'
down_revision: Union[str, None] = 'c483380ec75e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Financial Clinic fields and Product table."""
    
    # 1. Update customer_profiles table
    # Add new fields
    op.add_column('customer_profiles', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('customer_profiles', sa.Column('income_range', sa.String(50), nullable=True))
    
    # Note: We're NOT dropping 'age' and 'children' columns yet to maintain backward compatibility
    # They will be deprecated but kept for migration period
    
    # Add index for date_of_birth for age calculations
    op.create_index('ix_customer_profiles_date_of_birth', 'customer_profiles', ['date_of_birth'])
    
    # 2. Update survey_responses table
    # Note: survey_version column already exists, skip adding it
    # Just create index if it doesn't exist
    try:
        op.create_index('ix_survey_responses_survey_version', 'survey_responses', ['survey_version'])
    except:
        pass  # Index may already exist
    
    # 3. Create products table for Financial Clinic recommendations
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('category', sa.String(100), nullable=False, index=True),
        sa.Column('status_level', sa.String(50), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=False),
        
        # Demographic filters
        sa.Column('nationality_filter', sa.String(50), nullable=True, index=True),
        sa.Column('gender_filter', sa.String(20), nullable=True, index=True),
        sa.Column('children_filter', sa.String(20), nullable=True),
        
        # Priority and status
        sa.Column('priority', sa.Integer(), default=1, index=True),
        sa.Column('active', sa.Boolean(), default=True, index=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    """Rollback Financial Clinic changes."""
    
    # Drop products table
    op.drop_table('products')
    
    # Remove survey_version index (column stays as it was there before)
    try:
        op.drop_index('ix_survey_responses_survey_version', 'survey_responses')
    except:
        pass
    
    # Remove new customer_profiles columns
    op.drop_index('ix_customer_profiles_date_of_birth', 'customer_profiles')
    op.drop_column('customer_profiles', 'income_range')
    op.drop_column('customer_profiles', 'date_of_birth')
