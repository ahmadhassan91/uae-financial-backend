"""merge_migration_heads

Revision ID: 4b6e9065d93a
Revises: 6fe63e174eb9, add_bilingual_variations
Create Date: 2025-11-12 22:09:06.486748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b6e9065d93a'
down_revision: Union[str, None] = ('6fe63e174eb9', 'add_bilingual_variations')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
