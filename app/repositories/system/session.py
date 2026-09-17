"""
Session repo.
"""

from uuid import UUID

from sqlalchemy import select

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

    async def get_by_user_id(self, user_id: UUID) -> Session | None:
        """Find session by user_id."""
        result = await self.db.execute(select(Session).where(Session.user_id == user_id))
        return result.scalar_one_or_none()
