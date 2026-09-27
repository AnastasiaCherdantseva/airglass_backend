"""
Session repo.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select

from app.models import Session
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.dto import SessionInput, SessionOutput


class SessionRepository(BaseIdRepository[Session]):
    model = Session

    async def get_by_token_hash(self, token_hash: str) -> Session | None:
        """Find session by token."""
        result = await self.db.execute(select(Session).where(Session.token_hash == token_hash))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> list[Session]:
        """Find all sessions of the given user."""
        result = await self.db.execute(select(Session).where(Session.user_id == user_id))
        return list(result.scalars().all())

    async def delete_expired(self, time: datetime) -> int:
        """Delete all sessions where expired less then current time."""
        stmt = delete(Session).where(Session.expires_at < time)
        result = await self.db.execute(stmt)
        await self.flush()
        return result.rowcount

    async def delete_by_user_id(self, user_id: UUID) -> int:
        """Delete all sessions of the given user."""
        stmt = delete(Session).where(Session.user_id == user_id)
        result = await self.db.execute(stmt)
        await self.flush()
        return result.rowcount

    async def delete_by_token_hash(self, token_hash: str) -> bool:
        """Delete session by token."""
        stmt = delete(Session).where(Session.token_hash == token_hash)
        result = await self.db.execute(stmt)
        await self.flush()
        return result.rowcount > 0

    async def create(self, data: SessionInput) -> SessionOutput:
        now = datetime.now(UTC)
        new_session = Session(
            user_id=data.user_id,
            token_hash=data.token_hash,
            expires_at=data.expires_at,
            last_used_at=now,
            user_agent=data.user_agent,
            ip_address=data.ip_address,
        )
        self.add(new_session)
        await self.flush()
        return SessionOutput(
            user_id=new_session.user_id,
            token_hash=new_session.token_hash,
            expires_at=new_session.expires_at,
            user_agent=new_session.user_agent,
            ip_address=new_session.ip_address,
            id=new_session.id,
        )
