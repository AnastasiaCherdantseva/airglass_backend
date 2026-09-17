"""
Tests for SessionRepository.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_session_token
from app.models import Session
from app.repositories.system.session import SessionRepository


async def test_get_by_token(db_session: AsyncSession, session: dict[str, Session | str]) -> None:
    """
    get_by_token finds an existing session by its raw token.
    """
    repo = SessionRepository(db_session)
    token = session["token"]
    session_obj = session["data"]
    found = await repo.get_by_token(token)

    # ADR-AUTH-006: session has these fields.
    assert found is not None
    assert found.id == session_obj.id
    assert found.user_id == session_obj.user_id
    # ADR-AUTH-008: token_hash stores the hash, not the raw token.
    assert found.token_hash == hash_session_token(token)
    assert found.expires_at == session_obj.expires_at
    assert found.last_used_at == session_obj.last_used_at
    assert found.user_agent is None
    assert found.ip_address is None


async def test_get_by_user_id(db_session: AsyncSession, session: dict[str, Session | str]) -> None:
    """
    get_by_user_id finds an existing sessions by user_id.
    """
    repo = SessionRepository(db_session)
    token = session["token"]
    session_obj = session["data"]
    found = await repo.get_by_user_id(session_obj.user_id)

    assert found is not None
    # BR-AUTH-003: A user can have multiple active sessions.
    assert len(found) == 1

    # ADR-AUTH-006: session has these fields.
    s = found[0]
    assert s.id == session_obj.id
    assert s.user_id == session_obj.user_id
    # ADR-AUTH-008: token_hash stores the hash, not the raw token.
    assert s.token_hash == hash_session_token(token)
    assert s.expires_at == session_obj.expires_at
    assert s.last_used_at == session_obj.last_used_at
    assert s.user_agent is None
    assert s.ip_address is None
