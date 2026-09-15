from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


async def app_error_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    return _error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = []

    for error in exc.errors():
        location = ".".join(
            str(part)
            for part in error.get("loc", [])
        )

        errors.append(
            {
                "location": location,
                "message": error.get(
                    "msg",
                    "Invalid value",
                ),
                "type": error.get(
                    "type",
                    "validation_error",
                ),
            }
        )

    return _error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details={
            "errors": errors,
        },
    )


async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return _error_response(
        status_code=500,
        code="INTERNAL_ERROR",
        message="An unexpected error occurred",
    )