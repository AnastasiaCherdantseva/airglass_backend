"""
Fake-реализация SessionRepository для юнит-тестов.

In-memory: хранит сессии в словаре, не ходит в БД.
Структурно подходит под SessionReadRepositoryProtocol и
SessionWriteRepositoryProtocol — наследование не нужно.
"""

from datetime import datetime
from uuid import UUID, uuid4

from app.core.security import hash_session_token
from app.models.system import Session


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

    async def get_by_token(self, token: str) -> Session | None:
        """Найти по сырому токену (хеширует и ищет по token_hash)."""
        token_hash = hash_session_token(token)
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

    async def delete_by_token(self, token: str) -> None:
        """Удалить сессию по сырому токену."""
        token_hash = hash_session_token(token)
        for sid in list(self.sessions.keys()):
            if self.sessions[sid].token_hash == token_hash:
                del self.sessions[sid]

    async def delete_by_user_id(self, user_id: UUID) -> None:
        """Удалить все сессии пользователя."""
        for sid in list(self.sessions.keys()):
            if self.sessions[sid].user_id == user_id:
                del self.sessions[sid]

    async def delete_expired(self, now: datetime) -> int:
        """Удалить истёкшие сессии. Возвращает количество удалённых."""
        expired = [sid for sid, s in self.sessions.items() if s.expires_at < now]
        for sid in expired:
            del self.sessions[sid]
        return len(expired)

    async def flush(self) -> None:
        """No-op: в памяти всё уже на месте."""
        pass
