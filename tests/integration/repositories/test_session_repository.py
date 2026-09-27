"""
Tests for SessionRepository.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_session_token
from app.models import Session
from app.models.system.user import User
from app.repositories.protocols.dto.system.session import SessionInput
from app.repositories.system.session import SessionRepository


async def test_get_by_token(db_session: AsyncSession, session: dict[str, Session | str]) -> None:
    """
    get_by_token finds an existing session by its raw token.
    """
    repo = SessionRepository(db_session)
    token_hash = session["token_hash"]
    session_obj = session["data"]
    found = await repo.get_by_token(token_hash)

    # ADR-AUTH-006: session has these fields.
    assert found is not None
    assert found.id == session_obj.id
    assert found.user_id == session_obj.user_id
    assert found.expires_at == session_obj.expires_at
    assert found.last_used_at == session_obj.last_used_at
    assert found.user_agent is None
    assert found.ip_address is None


async def test_get_by_token_is_none(db_session: AsyncSession) -> None:
    """
    returns None when token not found
    """
    repo = SessionRepository(db_session)
    found = await repo.get_by_token("someToken")

    assert found is None


async def test_get_by_user_id(db_session: AsyncSession, sessions: dict[str, Session | str]) -> None:
    """
    get_by_user_id finds an existing sessions by user_id.
    """
    repo = SessionRepository(db_session)
    tokens = sessions["tokens"]
    token_hashes = sessions["tokens_hashes"]
    session_obj = sessions["data"][0]
    found = await repo.get_by_user_id(session_obj.user_id)

    assert found is not None
    # BR-AUTH-003: A user can have multiple active sessions.
    assert len(found) == len(sessions["data"])

    for index, s in enumerate(found):
        # ADR-AUTH-006: session has these fields.
        assert s.id == sessions["data"][index].id
        assert s.user_id == sessions["data"][index].user_id
        # ADR-AUTH-008: token_hash stores the hash, not the raw token.
        assert s.token_hash == token_hashes[index]
        assert s.token_hash != tokens[index]
        assert s.expires_at == sessions["data"][index].expires_at
        assert s.last_used_at == sessions["data"][index].last_used_at
        assert s.user_agent is None
        assert s.ip_address is None


async def test_get_by_user_id_not_found(
    db_session: AsyncSession, sessions: dict[str, Session | str]
) -> None:
    """
    get_by_user_id returns an empty list when user has no sessions.
    """
    repo = SessionRepository(db_session)
    fake_user_id = uuid.uuid4()
    found = await repo.get_by_user_id(fake_user_id)

    assert found == []


async def test_create_session(db_session: AsyncSession, user: User) -> None:
    """create persists a new session with hashed token and now as last_used_at."""
    repo = SessionRepository(db_session)
    now = datetime.now(UTC)
    data = SessionInput(
        user_id=user.id,
        token_hash=hash_session_token("token123"),
        expires_at=now + timedelta(days=7),
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1",
    )
    result = await repo.create(data)

    assert result.id is not None
    assert result.user_id == user.id
    assert result.token_hash == hash_session_token("token123")
    assert result.user_agent == "Mozilla/5.0"
    assert result.ip_address == "127.0.0.1"

    # Проверить, что сессия в БД
    found = await repo.get_by_token(hash_session_token("token123"))
    assert found is not None
    assert found.last_used_at is not None


async def test_delete_by_token_found(
    db_session: AsyncSession,
    session: dict,
) -> None:
    """delete_by_token returns True and removes the session."""
    repo = SessionRepository(db_session)
    token_hash = session["token_hash"]

    result = await repo.delete_by_token(token_hash)

    assert result is True
    found = await repo.get_by_token(token_hash)
    assert found is None


async def test_delete_by_token_not_found(
    db_session: AsyncSession,
) -> None:
    """delete_by_token returns False when token not found."""
    repo = SessionRepository(db_session)
    fake_hash = hash_session_token("nonexistent")

    result = await repo.delete_by_token(fake_hash)

    assert result is False


async def test_delete_by_token_does_not_touch_others(
    db_session: AsyncSession,
    sessions: dict,
) -> None:
    """delete_by_token removes only the target session."""
    repo = SessionRepository(db_session)
    tokens_hashes = sessions["tokens_hashes"]

    result = await repo.delete_by_token(tokens_hashes[0])
    assert result is True

    # Остальные две сессии на месте
    remaining = await repo.get_by_user_id(sessions["data"][0].user_id)
    assert len(remaining) == 2

    for s in remaining:
        assert s.token_hash in tokens_hashes[1:]


# ============================================================
# delete_by_user_id
# ============================================================


async def test_delete_by_user_id_removes_all(
    db_session: AsyncSession,
    sessions: dict,
) -> None:
    """delete_by_user_id removes all sessions of the user."""
    repo = SessionRepository(db_session)
    user_id = sessions["data"][0].user_id

    count = await repo.delete_by_user_id(user_id)

    assert count == 3
    found = await repo.get_by_user_id(user_id)
    assert found == []


async def test_delete_by_user_id_not_found(
    db_session: AsyncSession,
) -> None:
    """delete_by_user_id returns 0 for unknown user."""
    repo = SessionRepository(db_session)
    fake_user_id = uuid.uuid4()

    count = await repo.delete_by_user_id(fake_user_id)

    assert count == 0


async def test_delete_by_user_id_does_not_touch_other_users(
    db_session: AsyncSession,
    users: list[User],
    sessions_for_two_users: dict,
) -> None:
    """delete_by_user_id removes only the target user's sessions."""
    repo = SessionRepository(db_session)

    # Удалить сессии первого юзера
    count = await repo.delete_by_user_id(users[0].id)
    assert count == 3
    other_user_id = users[1].id
    # Сессия второго юзера на месте
    remaining = await repo.get_by_user_id(users[1].id)
    assert len(remaining) == 3
    expected_ids = set(sessions_for_two_users[other_user_id]["ids"])
    found_ids = {s.id for s in remaining}
    assert found_ids == expected_ids


# ============================================================
# delete_expired
# ============================================================


async def test_delete_expired_removes_only_expired(
    db_session: AsyncSession,
    sessions: dict,
) -> None:
    """delete_expired removes only sessions with expires_at < time."""
    repo = SessionRepository(db_session)
    now = datetime.now(UTC)

    # Сделать одну сессию просроченной
    expired = sessions["data"][0]
    expired.expires_at = now - timedelta(days=1)
    await db_session.flush()

    count = await repo.delete_expired(now)

    assert count == 1

    # Проверить, что оставшиеся — только не истёкшие
    remaining = await repo.get_by_user_id(expired.user_id)
    assert len(remaining) == 2
    for s in remaining:
        assert s.expires_at >= now


async def test_delete_expired_no_expired(
    db_session: AsyncSession,
    sessions: dict,
) -> None:
    """delete_expired returns 0 when nothing is expired."""
    repo = SessionRepository(db_session)
    now = datetime.now(UTC)

    count = await repo.delete_expired(now)

    assert count == 0


async def test_delete_expired_boundary_equal(
    db_session: AsyncSession,
    session: dict,
) -> None:
    """delete_expired does NOT remove session with expires_at == time."""
    repo = SessionRepository(db_session)
    session_obj = session["data"]
    threshold = session_obj.expires_at

    count = await repo.delete_expired(threshold)

    assert count == 0
    found = await repo.get_by_token(session["token_hash"])
    assert found is not None


async def test_delete_expired_removes_multiple(
    db_session: AsyncSession,
    user: User,
) -> None:
    """delete_expired removes all expired sessions."""
    repo = SessionRepository(db_session)
    now = datetime.now(UTC)

    # Создать 3 просроченные сессии
    expired_sessions = [
        Session(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=hash_session_token(f"expired_{i}"),
            expires_at=now - timedelta(days=i + 1),
            last_used_at=now - timedelta(days=i + 1),
        )
        for i in range(3)
    ]
    db_session.add_all(expired_sessions)
    await db_session.flush()

    count = await repo.delete_expired(now)

    assert count == 3
    remaining = await repo.get_by_user_id(user.id)
    assert remaining == []
