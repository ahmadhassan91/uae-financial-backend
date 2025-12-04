"""Add scheduled_emails table

Revision ID: add_scheduled_emails
Revises: 75eceb034b5b
Create Date: 2025-12-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_scheduled_emails'
down_revision = '75eceb034b5b'  # Points to the latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create scheduled_emails table
    op.create_table(
        'scheduled_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recipient_emails', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('scheduled_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status_filter', sa.String(length=20), nullable=True),
        sa.Column('source_filter', sa.String(length=50), nullable=True),
        sa.Column('date_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_to', sa.DateTime(timezone=True), nullable=True),
        sa.Column('job_id', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
   # Create indexes
    op.create_index('ix_scheduled_emails_id', 'scheduled_emails', ['id'], unique=False)
    op.create_index('ix_scheduled_emails_scheduled_datetime', 'scheduled_emails', ['scheduled_datetime'], unique=False)
    op.create_index('ix_scheduled_emails_job_id', 'scheduled_emails', ['job_id'], unique=True)
    op.create_index('ix_scheduled_emails_status', 'scheduled_emails', ['status'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_scheduled_emails_status', table_name='scheduled_emails')
    op.drop_index('ix_scheduled_emails_job_id', table_name='scheduled_emails')
    op.drop_index('ix_scheduled_emails_scheduled_datetime', table_name='scheduled_emails')
    op.drop_index('ix_scheduled_emails_id', table_name='scheduled_emails')
    
    # Drop table
    op.drop_table('scheduled_emails')
