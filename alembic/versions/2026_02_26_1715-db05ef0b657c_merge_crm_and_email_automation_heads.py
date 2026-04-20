"""merge crm and email automation heads

Revision ID: db05ef0b657c
Revises: 702b4b28dfa0, e4a5b59d6cb6
Create Date: 2026-02-26 17:15:17.748205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db05ef0b657c'
down_revision: Union[str, None] = ('702b4b28dfa0', 'e4a5b59d6cb6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
