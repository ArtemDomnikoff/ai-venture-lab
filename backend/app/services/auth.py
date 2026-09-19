from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from app.repositories.user import UserRepository
from app.repositories.user_session import UserSessionRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.security.password import (
    hash_password,
    verify_password,
)


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.user_repository = UserRepository(
            session,
        )
        self.session_repository = UserSessionRepository(
            session,
        )

    async def register(
        self,
        data: RegisterRequest,
    ):
        email = str(
            data.email,
        ).lower()

        existing_user = (
            await self.user_repository.get_by_email(
                email,
            )
        )

        if existing_user is not None:
            raise EmailAlreadyRegisteredError()

        user = await self.user_repository.create(
            email=email,
            password_hash=hash_password(
                data.password,
            ),
        )

        await self.session.commit()

        return user

    async def login(
        self,
        data: LoginRequest,
    ) -> tuple[object, str]:
        email = str(
            data.email,
        ).lower()

        user = await self.user_repository.get_by_email(
            email,
        )

        if (
            user is None
            or not verify_password(
                data.password,
                user.password_hash,
            )
        ):
            raise InvalidCredentialsError()

        token = secrets.token_urlsafe(32)

        token_hash = hashlib.sha256(
            token.encode(),
        ).hexdigest()

        settings = get_settings()

        expires_at = (
            datetime.now(UTC)
            + timedelta(
                days=settings.auth_session_days,
            )
        )

        await self.session_repository.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        await self.session.commit()

        return user, token

    async def logout(
        self,
        token: str,
    ) -> None:
        token_hash = hashlib.sha256(
            token.encode(),
        ).hexdigest()

        await self.session_repository.delete_by_token_hash(
            token_hash,
        )

        await self.session.commit()
