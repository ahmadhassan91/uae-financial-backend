"""add_question_variation_and_localization_schema

Revision ID: af977425d8d6
Revises: 8bcd32d4afae
Create Date: 2025-10-03 18:15:26.269681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af977425d8d6'
down_revision: Union[str, None] = '8bcd32d4afae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if tables exist and create only if they don't
    connection = op.get_bind()
    
    # Check if question_variations table exists
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'question_variations'
        );
    """))
    if not result.scalar():
        # Create question_variations table
        op.create_table(
            'question_variations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('base_question_id', sa.String(length=50), nullable=False),
            sa.Column('variation_name', sa.String(length=100), nullable=False),
            sa.Column('language', sa.String(length=5), nullable=False, server_default='en'),
            sa.Column('text', sa.Text(), nullable=False),
            sa.Column('options', sa.JSON(), nullable=False),
            sa.Column('demographic_rules', sa.JSON(), nullable=True),
            sa.Column('company_ids', sa.JSON(), nullable=True),
            sa.Column('factor', sa.String(length=50), nullable=False),
            sa.Column('weight', sa.Integer(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes for question_variations
        op.create_index('idx_question_variations_base_id', 'question_variations', ['base_question_id'])
        op.create_index('idx_question_variations_language', 'question_variations', ['language'])
        op.create_index('idx_question_variations_active', 'question_variations', ['is_active'])
    
    # Check if demographic_rules table exists
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'demographic_rules'
        );
    """))
    if not result.scalar():
        # Create demographic_rules table
        op.create_table(
            'demographic_rules',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('conditions', sa.JSON(), nullable=False),
            sa.Column('actions', sa.JSON(), nullable=False),
            sa.Column('priority', sa.Integer(), nullable=False, server_default='100'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes for demographic_rules
        op.create_index('idx_demographic_rules_priority', 'demographic_rules', ['priority', 'is_active'])
    
    # Check if localized_content table exists
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'localized_content'
        );
    """))
    if not result.scalar():
        # Create localized_content table
        op.create_table(
            'localized_content',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('content_type', sa.String(length=50), nullable=False),
            sa.Column('content_id', sa.String(length=100), nullable=False),
            sa.Column('language', sa.String(length=5), nullable=False),
            sa.Column('title', sa.String(length=500), nullable=True),
            sa.Column('text', sa.Text(), nullable=False),
            sa.Column('options', sa.JSON(), nullable=True),
            sa.Column('extra_data', sa.JSON(), nullable=True),
            sa.Column('version', sa.String(length=10), nullable=False, server_default='1.0'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes for localized_content
        op.create_index('idx_localized_content_lookup', 'localized_content', ['content_type', 'content_id', 'language'])
        op.create_index('idx_localized_content_active', 'localized_content', ['is_active'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_localized_content_active', table_name='localized_content')
    op.drop_index('idx_localized_content_lookup', table_name='localized_content')
    op.drop_index('idx_demographic_rules_priority', table_name='demographic_rules')
    op.drop_index('idx_question_variations_active', table_name='question_variations')
    op.drop_index('idx_question_variations_language', table_name='question_variations')
    op.drop_index('idx_question_variations_base_id', table_name='question_variations')
    
    # Drop tables
    op.drop_table('localized_content')
    op.drop_table('demographic_rules')
    op.drop_table('question_variations')
