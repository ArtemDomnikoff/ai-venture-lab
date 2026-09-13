import uuid
from datetime import datetime

from typing import TYPE_CHECKING

from app.domain.enums import ProjectStatus

if TYPE_CHECKING:
    from app.models.run import Run
from sqlalchemy import DateTime, String, Text, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    idea: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(
            ProjectStatus,
            name="project_status",
            native_enum=True,
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
        default=ProjectStatus.DRAFT,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    runs: Mapped[list["Run"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )