from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_user,
    get_rate_limiter,
    get_session,
)
from app.core.config import get_settings
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.security.rate_limit import (
    RateLimiter,
    email_rate_limit_key,
)
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def set_session_cookie(
    response: Response,
    token: str,
) -> None:
    settings = get_settings()

    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        max_age=settings.auth_session_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
    )


@router.post(
    "/register",
    response_model=UserResponse,
)
async def register(
    data: RegisterRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
) -> UserResponse:
    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    await rate_limiter.enforce(
        key=f"auth:register:ip:{client_ip}",
        limit=5,
        window_seconds=600,
    )
    service = AuthService(session)

    user = await service.register(data)

    login_data = LoginRequest(
        email=data.email,
        password=data.password,
    )

    user, token = await service.login(
        login_data,
    )

    set_session_cookie(
        response,
        token,
    )

    return user


@router.post(
    "/login",
    response_model=UserResponse,
)
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
) -> UserResponse:
    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    await rate_limiter.enforce(
        key=f"auth:login:ip:{client_ip}",
        limit=10,
        window_seconds=300,
    )

    await rate_limiter.enforce(
        key=email_rate_limit_key(
            data.email,
        ),
        limit=5,
        window_seconds=300,
    )
    service = AuthService(session)

    user, token = await service.login(data)

    set_session_cookie(
        response,
        token,
    )

    return user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> None:
    settings = get_settings()

    token = request.cookies.get(
        settings.auth_cookie_name,
    )

    if token:
        service = AuthService(session)

        await service.logout(token)

    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return current_user
