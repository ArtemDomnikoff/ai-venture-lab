from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_session import UserSession


class UserSessionRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> UserSession:
        user_session = UserSession(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.session.add(user_session)

        await self.session.flush()

        return user_session

    async def get_by_token_hash(
        self,
        token_hash: str,
    ) -> UserSession | None:
        result = await self.session.execute(
            select(UserSession)
            .where(
                UserSession.token_hash == token_hash,
            )
        )

        return result.scalar_one_or_none()

    async def delete_by_token_hash(
        self,
        token_hash: str,
    ) -> None:
        await self.session.execute(
            delete(UserSession).where(
                UserSession.token_hash == token_hash,
            )
        )
