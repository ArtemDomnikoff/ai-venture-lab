"""add unique active run per project

Revision ID: c4b7e1a2d9f3
Revises: e02e3b1c91b3
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4b7e1a2d9f3"
down_revision: str | Sequence[str] | None = "e02e3b1c91b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX uq_runs_project_active
        ON runs (project_id)
        WHERE status IN ('queued', 'running')
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS uq_runs_project_active
        """
    )
