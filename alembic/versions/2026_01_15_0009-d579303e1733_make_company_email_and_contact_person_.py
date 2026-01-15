"""make_company_email_and_contact_person_nullable_in_company_trackers

Revision ID: d579303e1733
Revises: add_enable_company_field_ops
Create Date: 2026-01-15 00:09:09.044419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd579303e1733'
down_revision: Union[str, None] = 'add_enable_company_field_ops'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make company_email and contact_person nullable in company_trackers table
    op.alter_column('company_trackers', 'company_email',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('company_trackers', 'contact_person',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)


def downgrade() -> None:
    # Revert to non-nullable (only if data allows)
    op.alter_column('company_trackers', 'contact_person',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
    op.alter_column('company_trackers', 'company_email',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
