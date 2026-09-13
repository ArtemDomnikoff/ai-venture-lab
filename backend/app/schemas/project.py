import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from app.domain.enums import ProjectStatus


class ProjectCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    idea: str = Field(
        min_length=10,
    )


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