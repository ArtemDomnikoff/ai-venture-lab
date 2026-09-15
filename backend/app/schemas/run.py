from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import RunStatus


class RunResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: uuid.UUID
    project_id: uuid.UUID
    status: RunStatus

    progress: dict[str, str]
    current_node: str | None

    started_at: datetime | None
    finished_at: datetime | None

    result: dict | None
    error: str | None

    created_at: datetime