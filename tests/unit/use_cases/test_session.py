"""
session use-case test.

"""

import pytest

from app.core.exceptions import PermissionDeniedError
from app.core.security import hash_session_token
from app.models.system import Session, User
from app.use_cases.session.create_session import create_session
from tests.unit.fakes.session_repository import FakeSessionRepository
from tests.unit.fakes.user_repository import FakeUserRepository


async def test_create_session_for_active_user(user_in_memory: User) -> None:
    """create_session returns a token for an active user."""
    fake_session_repo = FakeSessionRepository()
    fake_user_repo = FakeUserRepository([user_in_memory])

    result = await create_session(
        user_in_memory.id, sessions=fake_session_repo, users=fake_user_repo
    )

    assert len(fake_session_repo.sessions) == 1
    # BR-AUTH-012: token is a string returned to the client
    assert isinstance(result, str)
    assert len(result) > 20

    created = next(iter(fake_session_repo.sessions.values()))

    assert created.token_hash == hash_session_token(result)
    # ADR-AUTH-008
    assert created.token_hash != result
    assert created.user_id == user_in_memory.id
    assert created.ip_address is None
    assert created.user_agent is None


async def test_create_session_for_inactive_user(inactive_user_in_memory: User) -> None:
    """create_session raises PermissionDeniedError for an inactive user."""
    fake_session_repo = FakeSessionRepository()
    fake_user_repo = FakeUserRepository([inactive_user_in_memory])

    # BR-AUTH-013: if in user is_active = false, session does not created.
    with pytest.raises(PermissionDeniedError):
        await create_session(
            inactive_user_in_memory.id, sessions=fake_session_repo, users=fake_user_repo
        )

    assert len(fake_session_repo.sessions) == 0


async def test_create_another_session_active_user(
    user_in_memory: User, session_in_memory: dict[str, Session | str]
) -> None:
    """create_session adds another session for an active user."""
    fake_session_repo = FakeSessionRepository([session_in_memory["data"]])
    fake_user_repo = FakeUserRepository([user_in_memory])

    result = await create_session(
        user_in_memory.id, sessions=fake_session_repo, users=fake_user_repo
    )

    # BR-AUTH-003: user can have several sessions
    assert len(fake_session_repo.sessions) == 2

    # BR-AUTH-012: token is a string returned to the client
    assert isinstance(result, str)
    assert len(result) > 20

    sessions = list(fake_session_repo.sessions.values())
    created = sessions[1]

    assert created.token_hash == hash_session_token(result)
    # ADR-AUTH-008
    assert created.token_hash != result
    assert created.user_id == user_in_memory.id
    assert created.ip_address is None
    assert created.user_agent is None


async def test_create_another_session_inactive_user(
    inactive_user_in_memory: User, session_in_memory: dict[str, Session | str]
) -> None:
    """
    create_session raises PermissionDeniedError for an inactive user with existing sessions.
    """
    fake_session_repo = FakeSessionRepository([session_in_memory["data"]])
    fake_user_repo = FakeUserRepository([inactive_user_in_memory])

    # BR-AUTH-013: if in user is_active = false, session does not created.
    with pytest.raises(PermissionDeniedError):
        await create_session(
            inactive_user_in_memory.id, sessions=fake_session_repo, users=fake_user_repo
        )

    assert len(fake_session_repo.sessions) == 1
