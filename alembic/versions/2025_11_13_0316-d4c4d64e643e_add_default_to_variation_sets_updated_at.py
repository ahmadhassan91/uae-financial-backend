"""add_default_to_variation_sets_updated_at

Revision ID: d4c4d64e643e
Revises: 95da3f14bc08
Create Date: 2025-11-13 03:16:56.978057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4c4d64e643e'
down_revision: Union[str, None] = '95da3f14bc08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add server_default to updated_at column in variation_sets table
    op.alter_column('variation_sets', 'updated_at',
                    server_default=sa.text('now()'),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)


def downgrade() -> None:
    # Remove server_default from updated_at column
    op.alter_column('variation_sets', 'updated_at',
                    server_default=None,
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)
