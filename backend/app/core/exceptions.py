from __future__ import annotations

from typing import Any


class AppError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)

        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ProjectNotFoundError(AppError):
    def __init__(
        self,
        project_id: str,
    ) -> None:
        super().__init__(
            code="PROJECT_NOT_FOUND",
            message="Project not found",
            status_code=404,
            details={
                "project_id": project_id,
            },
        )


class RunNotFoundError(AppError):
    def __init__(
        self,
        run_id: str,
    ) -> None:
        super().__init__(
            code="RUN_NOT_FOUND",
            message="Run not found",
            status_code=404,
            details={
                "run_id": run_id,
            },
        )


class RunInvalidStateError(AppError):
    def __init__(
        self,
        *,
        run_id: str,
        current_status: str,
        target_status: str,
    ) -> None:
        super().__init__(
            code="RUN_INVALID_STATE",
            message="Invalid run state transition",
            status_code=409,
            details={
                "run_id": run_id,
                "current_status": current_status,
                "target_status": target_status,
            },
        )


class RunAlreadyRunningError(AppError):
    def __init__(
        self,
        project_id: str,
    ) -> None:
        super().__init__(
            code="RUN_ALREADY_RUNNING",
            message="Project already has an active analysis run",
            status_code=409,
            details={
                "project_id": project_id,
            },
        )


class AnalysisNotReadyError(AppError):
    def __init__(
        self,
        *,
        run_id: str,
        status: str,
    ) -> None:
        super().__init__(
            code="ANALYSIS_NOT_READY",
            message="Analysis result is not ready",
            status_code=409,
            details={
                "run_id": run_id,
                "status": status,
            },
        )


class AnalysisFailedError(AppError):
    def __init__(
        self,
        *,
        run_id: str,
        error: str | None = None,
    ) -> None:
        details: dict[str, Any] = {
            "run_id": run_id,
        }

        if error:
            details["error"] = error

        super().__init__(
            code="ANALYSIS_FAILED",
            message="Analysis failed",
            status_code=409,
            details=details,
        )


class ResultNotFoundError(AppError):
    def __init__(
        self,
        run_id: str,
    ) -> None:
        super().__init__(
            code="RESULT_NOT_FOUND",
            message="Analysis result not found",
            status_code=404,
            details={
                "run_id": run_id,
            },
        )