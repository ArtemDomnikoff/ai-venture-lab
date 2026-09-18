"""fix run status enum values

Revision ID: PUT_NEW_REVISION_HERE
Revises: PUT_PREVIOUS_REVISION_HERE
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e02e3b1c91b3"
down_revision: str | Sequence[str] | None = "02fdfdeed4d8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Fix run_status enum values to lowercase."""

    # 1. Remove the existing uppercase status values by replacing
    #    the enum with a temporary type.
    op.execute(
        """
        ALTER TYPE run_status RENAME TO run_status_old
        """
    )

    # 2. Create the enum with the values expected by Python.
    op.execute(
        """
        CREATE TYPE run_status AS ENUM (
            'queued',
            'running',
            'completed',
            'failed',
            'cancelled'
        )
        """
    )

    # 3. Convert the existing column values.
    op.execute(
        """
        ALTER TABLE runs
        ALTER COLUMN status TYPE run_status
        USING lower(status::text)::run_status
        """
    )

    # 4. Remove the old enum.
    op.execute(
        """
        DROP TYPE run_status_old
        """
    )


def downgrade() -> None:
    """Restore uppercase run_status enum values."""

    op.execute(
        """
        ALTER TYPE run_status RENAME TO run_status_old
        """
    )

    op.execute(
        """
        CREATE TYPE run_status AS ENUM (
            'QUEUED',
            'RUNNING',
            'COMPLETED',
            'FAILED',
            'CANCELLED'
        )
        """
    )

    op.execute(
        """
        ALTER TABLE runs
        ALTER COLUMN status TYPE run_status
        USING upper(status::text)::run_status
        """
    )

    op.execute(
        """
        DROP TYPE run_status_old
        """
    )
