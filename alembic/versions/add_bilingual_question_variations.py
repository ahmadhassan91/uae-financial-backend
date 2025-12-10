"""Add bilingual support to question variations

Revision ID: add_bilingual_variations
Revises: add_company_tracking_fc
Create Date: 2025-11-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = 'add_bilingual_variations'
down_revision = 'add_company_tracking_fc'  # Parent: add_company_tracking_to_financial_clinic
branch_labels = None
depends_on = None


def upgrade():
    """Add bilingual text fields to question_variations table."""
    
    # Add new bilingual columns
    op.add_column('question_variations', sa.Column('text_en', sa.Text(), nullable=True))
    op.add_column('question_variations', sa.Column('text_ar', sa.Text(), nullable=True))
    
    # Migrate existing data: copy 'text' to 'text_en' for all existing variations
    op.execute("""
        UPDATE question_variations 
        SET text_en = text 
        WHERE text IS NOT NULL AND text_en IS NULL
    """)
    
    # Add placeholder for text_ar (needs manual translation)
    op.execute("""
        UPDATE question_variations 
        SET text_ar = '[Translation needed]' 
        WHERE text_ar IS NULL
    """)
    
    # Note: The 'text' column is kept for backward compatibility
    # The 'language' column is kept but will be set to 'both' for new variations


def downgrade():
    """Remove bilingual text fields from question_variations table."""
    
    op.drop_column('question_variations', 'text_ar')
    op.drop_column('question_variations', 'text_en')
