"""enhance_existing_models_for_advanced_features

Revision ID: 68cc0c8f7a83
Revises: af977425d8d6
Create Date: 2025-10-03 18:25:40.433254

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68cc0c8f7a83'
down_revision: Union[str, None] = 'af977425d8d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enhance CustomerProfile model with additional demographic fields
    op.add_column('customer_profiles', sa.Column('education_level', sa.String(length=50), nullable=True))
    op.add_column('customer_profiles', sa.Column('years_in_uae', sa.Integer(), nullable=True))
    op.add_column('customer_profiles', sa.Column('family_status', sa.String(length=50), nullable=True))
    op.add_column('customer_profiles', sa.Column('housing_status', sa.String(length=50), nullable=True))
    op.add_column('customer_profiles', sa.Column('banking_relationship', sa.String(length=100), nullable=True))
    op.add_column('customer_profiles', sa.Column('investment_experience', sa.String(length=50), nullable=True))
    op.add_column('customer_profiles', sa.Column('financial_goals', sa.JSON(), nullable=True))
    op.add_column('customer_profiles', sa.Column('preferred_communication', sa.String(length=20), nullable=False, server_default='email'))
    op.add_column('customer_profiles', sa.Column('islamic_finance_preference', sa.Boolean(), nullable=False, server_default='false'))
    
    # Enhance SurveyResponse model to track question variations and language
    op.add_column('survey_responses', sa.Column('question_set_id', sa.String(length=100), nullable=True))
    op.add_column('survey_responses', sa.Column('question_variations_used', sa.JSON(), nullable=True))
    op.add_column('survey_responses', sa.Column('demographic_rules_applied', sa.JSON(), nullable=True))
    op.add_column('survey_responses', sa.Column('language', sa.String(length=5), nullable=False, server_default='en'))
    op.add_column('survey_responses', sa.Column('company_tracker_id', sa.Integer(), nullable=True))
    op.add_column('survey_responses', sa.Column('email_sent', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('survey_responses', sa.Column('pdf_generated', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('survey_responses', sa.Column('report_downloads', sa.Integer(), nullable=False, server_default='0'))
    
    # Add foreign key constraint for company_tracker_id
    op.create_foreign_key(
        'fk_survey_responses_company_tracker',
        'survey_responses', 'company_trackers',
        ['company_tracker_id'], ['id']
    )
    
    # Enhance CompanyTracker model with company-specific fields
    op.add_column('company_trackers', sa.Column('question_set_config', sa.JSON(), nullable=True))
    op.add_column('company_trackers', sa.Column('demographic_rules_config', sa.JSON(), nullable=True))
    op.add_column('company_trackers', sa.Column('localization_settings', sa.JSON(), nullable=True))
    op.add_column('company_trackers', sa.Column('report_branding', sa.JSON(), nullable=True))
    op.add_column('company_trackers', sa.Column('admin_users', sa.JSON(), nullable=True))
    
    # Create indexes for performance optimization
    op.create_index('idx_survey_responses_company', 'survey_responses', ['company_tracker_id', 'created_at'])
    op.create_index('idx_survey_responses_language', 'survey_responses', ['language'])
    op.create_index('idx_customer_profiles_demographics', 'customer_profiles', ['nationality', 'emirate', 'age'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_customer_profiles_demographics', table_name='customer_profiles')
    op.drop_index('idx_survey_responses_language', table_name='survey_responses')
    op.drop_index('idx_survey_responses_company', table_name='survey_responses')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_survey_responses_company_tracker', 'survey_responses', type_='foreignkey')
    
    # Remove columns from CompanyTracker
    op.drop_column('company_trackers', 'admin_users')
    op.drop_column('company_trackers', 'report_branding')
    op.drop_column('company_trackers', 'localization_settings')
    op.drop_column('company_trackers', 'demographic_rules_config')
    op.drop_column('company_trackers', 'question_set_config')
    
    # Remove columns from SurveyResponse
    op.drop_column('survey_responses', 'report_downloads')
    op.drop_column('survey_responses', 'pdf_generated')
    op.drop_column('survey_responses', 'email_sent')
    op.drop_column('survey_responses', 'company_tracker_id')
    op.drop_column('survey_responses', 'language')
    op.drop_column('survey_responses', 'demographic_rules_applied')
    op.drop_column('survey_responses', 'question_variations_used')
    op.drop_column('survey_responses', 'question_set_id')
    
    # Remove columns from CustomerProfile
    op.drop_column('customer_profiles', 'islamic_finance_preference')
    op.drop_column('customer_profiles', 'preferred_communication')
    op.drop_column('customer_profiles', 'financial_goals')
    op.drop_column('customer_profiles', 'investment_experience')
    op.drop_column('customer_profiles', 'banking_relationship')
    op.drop_column('customer_profiles', 'housing_status')
    op.drop_column('customer_profiles', 'family_status')
    op.drop_column('customer_profiles', 'years_in_uae')
    op.drop_column('customer_profiles', 'education_level')
