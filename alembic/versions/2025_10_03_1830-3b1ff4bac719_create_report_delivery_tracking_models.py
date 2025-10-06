"""create_report_delivery_tracking_models

Revision ID: 3b1ff4bac719
Revises: 68cc0c8f7a83
Create Date: 2025-10-03 18:30:34.379840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b1ff4bac719'
down_revision: Union[str, None] = '68cc0c8f7a83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if tables exist and create only if they don't
    connection = op.get_bind()
    
    # Check if report_deliveries table exists
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'report_deliveries'
        );
    """))
    if not result.scalar():
        # Create report_deliveries table
        op.create_table(
            'report_deliveries',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('survey_response_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('delivery_type', sa.String(length=20), nullable=False),  # email, pdf_download
            sa.Column('delivery_status', sa.String(length=20), nullable=False),  # pending, sent, failed, downloaded
            sa.Column('recipient_email', sa.String(length=255), nullable=True),
            sa.Column('file_path', sa.String(length=500), nullable=True),  # For PDF files
            sa.Column('file_size', sa.Integer(), nullable=True),  # File size in bytes
            sa.Column('language', sa.String(length=5), nullable=False, server_default='en'),
            sa.Column('delivery_metadata', sa.JSON(), nullable=True),  # Additional delivery info
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Add foreign key constraints for report_deliveries
        op.create_foreign_key(
            'fk_report_deliveries_survey_response',
            'report_deliveries', 'survey_responses',
            ['survey_response_id'], ['id']
        )
        op.create_foreign_key(
            'fk_report_deliveries_user',
            'report_deliveries', 'users',
            ['user_id'], ['id']
        )
        
        # Create indexes for report_deliveries
        op.create_index('idx_report_deliveries_survey_response', 'report_deliveries', ['survey_response_id'])
        op.create_index('idx_report_deliveries_user', 'report_deliveries', ['user_id'])
        op.create_index('idx_report_deliveries_status', 'report_deliveries', ['delivery_status'])
        op.create_index('idx_report_deliveries_type', 'report_deliveries', ['delivery_type'])
        op.create_index('idx_report_deliveries_created', 'report_deliveries', ['created_at'])
    
    # Check if report_access_logs table exists
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'report_access_logs'
        );
    """))
    if not result.scalar():
        # Create report_access_logs table for tracking downloads and views
        op.create_table(
            'report_access_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('report_delivery_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),  # Can be null for anonymous access
            sa.Column('access_type', sa.String(length=20), nullable=False),  # download, view, email_open
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.String(length=500), nullable=True),
            sa.Column('access_metadata', sa.JSON(), nullable=True),  # Additional access info
            sa.Column('accessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Add foreign key constraints for report_access_logs
        op.create_foreign_key(
            'fk_report_access_logs_delivery',
            'report_access_logs', 'report_deliveries',
            ['report_delivery_id'], ['id']
        )
        op.create_foreign_key(
            'fk_report_access_logs_user',
            'report_access_logs', 'users',
            ['user_id'], ['id']
        )
        
        # Create indexes for report_access_logs
        op.create_index('idx_report_access_logs_delivery', 'report_access_logs', ['report_delivery_id'])
        op.create_index('idx_report_access_logs_user', 'report_access_logs', ['user_id'])
        op.create_index('idx_report_access_logs_accessed', 'report_access_logs', ['accessed_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_report_access_logs_accessed', table_name='report_access_logs')
    op.drop_index('idx_report_access_logs_user', table_name='report_access_logs')
    op.drop_index('idx_report_access_logs_delivery', table_name='report_access_logs')
    op.drop_index('idx_report_deliveries_created', table_name='report_deliveries')
    op.drop_index('idx_report_deliveries_type', table_name='report_deliveries')
    op.drop_index('idx_report_deliveries_status', table_name='report_deliveries')
    op.drop_index('idx_report_deliveries_user', table_name='report_deliveries')
    op.drop_index('idx_report_deliveries_survey_response', table_name='report_deliveries')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_report_access_logs_user', 'report_access_logs', type_='foreignkey')
    op.drop_constraint('fk_report_access_logs_delivery', 'report_access_logs', type_='foreignkey')
    op.drop_constraint('fk_report_deliveries_user', 'report_deliveries', type_='foreignkey')
    op.drop_constraint('fk_report_deliveries_survey_response', 'report_deliveries', type_='foreignkey')
    
    # Drop tables
    op.drop_table('report_access_logs')
    op.drop_table('report_deliveries')
