"""
Tests for SessionRepository.
"""

import uuid

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
    assert found.token_hash != token
    assert found.expires_at == session_obj.expires_at
    assert found.last_used_at == session_obj.last_used_at
    assert found.user_agent is None
    assert found.ip_address is None


async def test_get_by_token_is_none(db_session: AsyncSession) -> None:
    """
    get_by_token finds an existing session by its raw token.
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
        assert s.token_hash == hash_session_token(tokens[index])
        assert s.expires_at == sessions["data"][index].expires_at
        assert s.last_used_at == sessions["data"][index].last_used_at
        assert s.user_agent is None
        assert s.ip_address is None


async def test_get_by_fake_user_id(
    db_session: AsyncSession, sessions: dict[str, Session | str]
) -> None:
    """
    get_by_user_id returns nullbale list if the user has no any sessions.
    """
    repo = SessionRepository(db_session)
    fake_user_id = uuid.uuid4()
    found = await repo.get_by_user_id(fake_user_id)

    assert found == []
