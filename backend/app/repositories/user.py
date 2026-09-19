from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            free_runs_remaining=3,
        )

        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def get_by_id(
        self,
        user_id: uuid.UUID,
    ) -> User | None:
        result = await self.session.execute(
            select(User).where(
                User.id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.session.execute(
            select(User).where(
                User.email == email,
            )
        )

        return result.scalar_one_or_none()

    async def consume_free_run(
        self,
        user_id: uuid.UUID,
    ) -> int | None:
        statement = (
            update(User)
            .where(
                User.id == user_id,
                User.free_runs_remaining > 0,
            )
            .values(
                free_runs_remaining=(
                    User.free_runs_remaining - 1
                ),
            )
            .returning(
                User.free_runs_remaining,
            )
        )

        result = await self.session.execute(
            statement,
        )

        return result.scalar_one_or_none()
