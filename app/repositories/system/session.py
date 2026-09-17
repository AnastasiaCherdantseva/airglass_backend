"""
Session repo.
"""

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
