"""add project status enum

Revision ID: 02fdfdeed4d8
Revises: d740d864ceeb
Create Date: 2026-09-13 22:31:50.060755
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "02fdfdeed4d8"
down_revision: str | Sequence[str] | None = "d740d864ceeb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


project_status_enum = postgresql.ENUM(
    "draft",
    "active",
    "archived",
    name="project_status",
)


def upgrade() -> None:
    """Upgrade schema."""
    project_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.alter_column(
        "projects",
        "status",
        existing_type=sa.VARCHAR(length=50),
        type_=project_status_enum,
        existing_nullable=False,
        postgresql_using="status::project_status",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "projects",
        "status",
        existing_type=project_status_enum,
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
        postgresql_using="status::varchar",
    )

    project_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )
