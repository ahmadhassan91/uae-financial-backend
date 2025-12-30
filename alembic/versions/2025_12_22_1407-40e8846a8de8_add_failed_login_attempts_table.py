"""add_failed_login_attempts_table

Revision ID: 40e8846a8de8
Revises: remove_arabic_periods
Create Date: 2025-12-22 14:07:39.678127

This migration adds the failed_login_attempts table for security audit compliance.
Used to track failed OTP/login attempts and implement account lockout.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '40e8846a8de8'
down_revision: Union[str, None] = 'remove_arabic_periods'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if table already exists (may have been auto-created)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'failed_login_attempts' not in tables:
        # Create failed_login_attempts table for account lockout tracking
        op.create_table(
            'failed_login_attempts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('identifier', sa.String(length=255), nullable=False),
            sa.Column('identifier_type', sa.String(length=20), nullable=False, server_default='email'),
            sa.Column('attempt_type', sa.String(length=50), nullable=False),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.String(length=500), nullable=True),
            sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('last_attempt_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes for efficient querying
        op.create_index('ix_failed_login_attempts_id', 'failed_login_attempts', ['id'])
        op.create_index('ix_failed_login_attempts_identifier', 'failed_login_attempts', ['identifier'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_failed_login_attempts_identifier', table_name='failed_login_attempts')
    op.drop_index('ix_failed_login_attempts_id', table_name='failed_login_attempts')
    
    # Drop the table
    op.drop_table('failed_login_attempts')
