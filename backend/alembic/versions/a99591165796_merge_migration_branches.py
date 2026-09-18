"""merge migration branches

Revision ID: a99591165796
Revises: c4b7e1a2d9f3, b83840cd09e7
Create Date: 2026-09-15 23:10:41.366868

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "a99591165796"
down_revision: str | Sequence[str] | None = ("c4b7e1a2d9f3", "b83840cd09e7")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
