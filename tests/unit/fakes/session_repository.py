"""
Fake-реализация SessionRepository для юнит-тестов.

In-memory: хранит сессии в словаре, не ходит в БД.
Структурно подходит под SessionReadRepositoryProtocol и
SessionWriteRepositoryProtocol — наследование не нужно.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.models.system import Session
from app.repositories.protocols.dto.system.session import (
    SessionInput,
    SessionOutput,
)


class FakeSessionRepository:
    """In-memory реализация SessionRepository."""

    def __init__(self, initial_sessions: list[Session] | None = None) -> None:
        self.sessions: dict[UUID, Session] = {}
        if initial_sessions:
            for s in initial_sessions:
                self.add(s)

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_by_id(self, session_id: UUID) -> Session | None:
        """Найти по id."""
        return self.sessions.get(session_id)

    async def get_by_token(self, token_hash: str) -> Session | None:
        """Найти по хешу токена."""
        return next(
            (s for s in self.sessions.values() if s.token_hash == token_hash),
            None,
        )

    async def get_by_user_id(self, user_id: UUID) -> list[Session]:
        """Найти все сессии пользователя."""
        return [s for s in self.sessions.values() if s.user_id == user_id]

    # ========================================
    # ЗАПИСЬ
    # ========================================

    def add(self, session: Session) -> None:
        """Добавить сессию в память."""
        if session.id is None:
            session.id = uuid4()
        self.sessions[session.id] = session

    async def delete(self, session: Session) -> None:
        """Удалить сессию из памяти."""
        self.sessions.pop(session.id, None)

    async def delete_by_token(self, token_hash: str) -> bool:
        """Удалить сессию по хешу токена."""
        for sid, s in list(self.sessions.items()):
            if s.token_hash == token_hash:
                del self.sessions[sid]
                return True
        return False

    async def delete_by_user_id(self, user_id: UUID) -> int:
        """Удалить все сессии пользователя. Возвращает количество."""
        ids = [sid for sid, s in self.sessions.items() if s.user_id == user_id]
        for sid in ids:
            del self.sessions[sid]
        return len(ids)

    async def delete_expired(self, now: datetime) -> int:
        """Удалить истёкшие сессии. Возвращает количество удалённых."""
        expired = [sid for sid, s in self.sessions.items() if s.expires_at < now]
        for sid in expired:
            del self.sessions[sid]
        return len(expired)

    async def create(self, data: SessionInput) -> SessionOutput:
        """Создать новую сессию в памяти."""
        now = datetime.now(UTC)
        session = Session(
            id=uuid4(),
            user_id=data.user_id,
            token_hash=data.token_hash,
            expires_at=data.expires_at,
            last_used_at=now,
            user_agent=data.user_agent,
            ip_address=data.ip_address,
        )
        self.sessions[session.id] = session
        return SessionOutput(
            id=session.id,
            user_id=session.user_id,
            token_hash=session.token_hash,
            expires_at=session.expires_at,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
        )

    async def flush(self) -> None:
        """No-op: в памяти всё уже на месте."""
        pass
