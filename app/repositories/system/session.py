"""
Session repo.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select

from app.core.security import hash_session_token
from app.models import Session
from app.repositories.base import BaseIdRepository


class SessionRepository(BaseIdRepository[Session]):
    model = Session

    async def get_by_token(self, token: str) -> Session | None:
        """Find session by token."""
        result = await self.db.execute(
            select(Session).where(Session.token_hash == hash_session_token(token))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> list[Session]:
        """Find all sessions of the given user."""
        result = await self.db.execute(select(Session).where(Session.user_id == user_id))
        return list(result.scalars().all())

    async def delete_expired(self, time: datetime) -> int:
        """Delete all sessions where expired less then current time."""
        stmt = delete(Session).where(Session.expires_at < time)
        result = await self.db.execute(stmt)
        return result.rowcount

    async def delete_by_user_id(self, user_id: UUID) -> int:
        """Delete all sessions of the given user."""
        stmt = delete(Session).where(Session.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.rowcount

    async def delete_by_token(self, token: str) -> bool:
        """Delete session by token."""
        stmt = delete(Session).where(Session.token_hash == hash_session_token(token))
        result = await self.db.execute(stmt)
        return result.rowcount > 0
