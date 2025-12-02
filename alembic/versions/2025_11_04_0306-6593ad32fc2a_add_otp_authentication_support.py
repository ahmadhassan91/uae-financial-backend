"""add_otp_authentication_support

Revision ID: 6593ad32fc2a
Revises: 69d35e0766b1
Create Date: 2025-11-04 03:06:38.161299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6593ad32fc2a'
down_revision: Union[str, None] = '69d35e0766b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create otp_codes table
    op.create_table(
        'otp_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=6), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('ix_otp_codes_email', 'otp_codes', ['email'])
    op.create_index('ix_otp_codes_email_expires', 'otp_codes', ['email', 'expires_at'])
    
    # Add email verification fields to users table
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True))
    
    # Backfill existing users as verified (they used DOB auth previously)
    op.execute("UPDATE users SET email_verified = true WHERE email IS NOT NULL")


def downgrade() -> None:
    # Remove email verification fields from users
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'email_verified')
    
    # Drop indexes
    op.drop_index('ix_otp_codes_email_expires', 'otp_codes')
    op.drop_index('ix_otp_codes_email', 'otp_codes')
    
    # Drop otp_codes table
    op.drop_table('otp_codes')
