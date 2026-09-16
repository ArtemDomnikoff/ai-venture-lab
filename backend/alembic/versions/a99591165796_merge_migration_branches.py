"""merge migration branches

Revision ID: a99591165796
Revises: c4b7e1a2d9f3, b83840cd09e7
Create Date: 2026-09-15 23:10:41.366868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a99591165796'
down_revision: Union[str, Sequence[str], None] = ('c4b7e1a2d9f3', 'b83840cd09e7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
