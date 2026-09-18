from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.domain.enums import ProjectStatus


class ProjectCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    idea: str = Field(
        min_length=10,
    )

    @field_validator("name", "idea")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value must not be blank")

        return value


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    idea: str | None = Field(
        default=None,
        min_length=10,
    )

    @field_validator("name", "idea")
    @classmethod
    def validate_not_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Value must not be blank")

        return value

    @model_validator(mode="after")
    def validate_not_empty(self) -> ProjectUpdate:
        if self.name is None and self.idea is None:
            raise ValueError(
                "At least one field must be provided",
            )

        return self


class ProjectResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: uuid.UUID
    name: str
    idea: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int = Field(
        ge=0,
    )
    page: int = Field(
        ge=1,
    )
    page_size: int = Field(
        ge=1,
        le=100,
    )
