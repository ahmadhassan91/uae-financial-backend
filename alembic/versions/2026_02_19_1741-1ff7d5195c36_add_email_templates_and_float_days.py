"""add email templates and float days

Revision ID: 1ff7d5195c36
Revises: 3c58242e993f
Create Date: 2026-02-19 17:41:57.753303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ff7d5195c36'
down_revision: Union[str, None] = '3c58242e993f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change columns to Float using explicit cast
    op.alter_column('email_automation_config', 'incomplete_days',
               existing_type=sa.Integer(),
               type_=sa.Float(),
               postgresql_using='incomplete_days::float')
    op.alter_column('email_automation_config', 'checkup_days',
               existing_type=sa.Integer(),
               type_=sa.Float(),
               postgresql_using='checkup_days::float')

    # Add template columns
    op.add_column('email_automation_config', sa.Column('incomplete_subject_en', sa.String(), nullable=True))
    op.add_column('email_automation_config', sa.Column('incomplete_subject_ar', sa.String(), nullable=True))
    op.add_column('email_automation_config', sa.Column('incomplete_body_en', sa.Text(), nullable=True))
    op.add_column('email_automation_config', sa.Column('incomplete_body_ar', sa.Text(), nullable=True))
    
    op.add_column('email_automation_config', sa.Column('checkup_subject_en', sa.String(), nullable=True))
    op.add_column('email_automation_config', sa.Column('checkup_subject_ar', sa.String(), nullable=True))
    op.add_column('email_automation_config', sa.Column('checkup_body_en', sa.Text(), nullable=True))
    op.add_column('email_automation_config', sa.Column('checkup_body_ar', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove template columns
    op.drop_column('email_automation_config', 'checkup_body_ar')
    op.drop_column('email_automation_config', 'checkup_body_en')
    op.drop_column('email_automation_config', 'checkup_subject_ar')
    op.drop_column('email_automation_config', 'checkup_subject_en')
    
    op.drop_column('email_automation_config', 'incomplete_body_ar')
    op.drop_column('email_automation_config', 'incomplete_body_en')
    op.drop_column('email_automation_config', 'incomplete_subject_ar')
    op.drop_column('email_automation_config', 'incomplete_subject_en')

    # Revert columns to Integer
    op.alter_column('email_automation_config', 'checkup_days',
               existing_type=sa.Float(),
               type_=sa.Integer(),
               postgresql_using='checkup_days::integer')
    op.alter_column('email_automation_config', 'incomplete_days',
               existing_type=sa.Float(),
               type_=sa.Integer(),
               postgresql_using='incomplete_days::integer')
