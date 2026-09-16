from fastapi import APIRouter

from app.api.routes.metrics import router as metrics_router
from app.api.routes.projects import router as projects_router
from app.api.routes.results import router as results_router
from app.api.routes.runs import (
    projects_router as project_runs_router,
    runs_router,
)


api_router = APIRouter(
    prefix="/api/v1",
)


api_router.include_router(
    projects_router,
)

api_router.include_router(
    project_runs_router,
)

api_router.include_router(
    runs_router,
)

api_router.include_router(
    results_router,
)

api_router.include_router(
    metrics_router,
)