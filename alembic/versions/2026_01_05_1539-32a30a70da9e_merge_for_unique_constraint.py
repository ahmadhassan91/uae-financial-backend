"""merge for unique constraint

Revision ID: 32a30a70da9e
Revises: 40e8846a8de8, a31796ca638c
Create Date: 2026-01-05 15:39:42.380629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32a30a70da9e'
down_revision: Union[str, None] = ('40e8846a8de8', 'a31796ca638c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
