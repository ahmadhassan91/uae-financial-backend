"""add_variation_sets_and_company_assignment

Revision ID: 95da3f14bc08
Revises: 4b6e9065d93a
Create Date: 2025-11-13 00:13:29.790275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95da3f14bc08'
down_revision: Union[str, None] = '4b6e9065d93a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create variation_sets table
    op.create_table(
        'variation_sets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('set_type', sa.String(length=50), nullable=False),  # 'industry', 'demographic', 'language', 'custom'
        sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Foreign keys for all 15 Financial Clinic questions
        sa.Column('q1_variation_id', sa.Integer(), nullable=False),
        sa.Column('q2_variation_id', sa.Integer(), nullable=False),
        sa.Column('q3_variation_id', sa.Integer(), nullable=False),
        sa.Column('q4_variation_id', sa.Integer(), nullable=False),
        sa.Column('q5_variation_id', sa.Integer(), nullable=False),
        sa.Column('q6_variation_id', sa.Integer(), nullable=False),
        sa.Column('q7_variation_id', sa.Integer(), nullable=False),
        sa.Column('q8_variation_id', sa.Integer(), nullable=False),
        sa.Column('q9_variation_id', sa.Integer(), nullable=False),
        sa.Column('q10_variation_id', sa.Integer(), nullable=False),
        sa.Column('q11_variation_id', sa.Integer(), nullable=False),
        sa.Column('q12_variation_id', sa.Integer(), nullable=False),
        sa.Column('q13_variation_id', sa.Integer(), nullable=False),
        sa.Column('q14_variation_id', sa.Integer(), nullable=False),
        sa.Column('q15_variation_id', sa.Integer(), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['q1_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q2_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q3_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q4_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q5_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q6_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q7_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q8_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q9_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q10_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q11_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q12_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q13_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q14_variation_id'], ['question_variations.id'], ),
        sa.ForeignKeyConstraint(['q15_variation_id'], ['question_variations.id'], ),
    )
    
    # Create indexes for better query performance
    op.create_index('ix_variation_sets_name', 'variation_sets', ['name'])
    op.create_index('ix_variation_sets_set_type', 'variation_sets', ['set_type'])
    op.create_index('ix_variation_sets_is_template', 'variation_sets', ['is_template'])
    op.create_index('ix_variation_sets_is_active', 'variation_sets', ['is_active'])
    
    # Add variation_set_id column to company_tracker table
    op.add_column(
        'company_trackers',
        sa.Column('variation_set_id', sa.Integer(), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_company_trackers_variation_set_id',
        'company_trackers',
        'variation_sets',
        ['variation_set_id'],
        ['id']
    )
    
    # Add index for better query performance
    op.create_index(
        'ix_company_trackers_variation_set_id',
        'company_trackers',
        ['variation_set_id']
    )


def downgrade() -> None:
    # Drop company_tracker foreign key and column
    op.drop_index('ix_company_trackers_variation_set_id', table_name='company_trackers')
    op.drop_constraint('fk_company_trackers_variation_set_id', 'company_trackers', type_='foreignkey')
    op.drop_column('company_trackers', 'variation_set_id')
    
    # Drop variation_sets indexes
    op.drop_index('ix_variation_sets_is_active', table_name='variation_sets')
    op.drop_index('ix_variation_sets_is_template', table_name='variation_sets')
    op.drop_index('ix_variation_sets_set_type', table_name='variation_sets')
    op.drop_index('ix_variation_sets_name', table_name='variation_sets')
    
    # Drop variation_sets table
    op.drop_table('variation_sets')
