"""add run progress tracking

Revision ID: b83840cd09e7
Revises: d4d31e40bafc
Create Date: 2026-09-15 20:47:23.876591
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b83840cd09e7"
down_revision: str | Sequence[str] | None = "d4d31e40bafc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "runs",
        sa.Column(
            "progress",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    op.add_column(
        "runs",
        sa.Column(
            "current_node",
            sa.String(),
            nullable=True,
        ),
    )

    op.alter_column(
        "runs",
        "progress",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column(
        "runs",
        "current_node",
    )

    op.drop_column(
        "runs",
        "progress",
    )
