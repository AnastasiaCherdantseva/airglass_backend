"""
Unit-тесты use case authenticate_user.
"""

import pytest

from app.core.exceptions import AuthenticationError
from app.core.security import hash_session_token
from app.models.system import User
from app.use_cases.system import authenticate_user
from tests.fixtures.users import TEST_PASSWORD
from tests.unit.fakes.session_repository import FakeSessionRepository
from tests.unit.fakes.user_repository import FakeUserRepository
from tests.unit.fakes.user_role_repository import FakeUserRoleRepository

# ============================================================
# ОШИБКИ
# ============================================================


async def test_user_not_found_raises(
    fake_sessions_repo: FakeSessionRepository,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Юзер не найден → AuthenticationError."""
    with pytest.raises(AuthenticationError):
        await authenticate_user(
            email="unknown@example.com",
            password=TEST_PASSWORD,
            sessions=fake_sessions_repo,
            users=fake_users_repo,
            user_roles=fake_user_roles_repo,
        )


async def test_user_inactive_raises(
    inactive_user_in_memory: User,
    fake_users_repo_inactive: FakeUserRepository,
    fake_sessions_repo: FakeSessionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Юзер неактивен → AuthenticationError."""
    with pytest.raises(AuthenticationError):
        await authenticate_user(
            email=inactive_user_in_memory.email,
            password=TEST_PASSWORD,
            sessions=fake_sessions_repo,
            users=fake_users_repo_inactive,
            user_roles=fake_user_roles_repo,
        )


async def test_wrong_password_raises(
    user_in_memory: User,
    fake_users_repo: FakeUserRepository,
    fake_sessions_repo: FakeSessionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Неверный пароль → AuthenticationError."""
    with pytest.raises(AuthenticationError):
        await authenticate_user(
            email=user_in_memory.email,
            password="wrongsecretsecretsecret",
            sessions=fake_sessions_repo,
            users=fake_users_repo,
            user_roles=fake_user_roles_repo,
        )


# ============================================================
# УСПЕХ
# ============================================================


async def test_success_returns_authenticated_user(
    users_in_memory: list[User],
    role_in_memory,
    fake_users_repo: FakeUserRepository,
    fake_sessions_repo: FakeSessionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Успешная аутентификация возвращает AuthenticatedUser."""
    user = users_in_memory[0]
    result = await authenticate_user(
        email=user.email,
        password=TEST_PASSWORD,
        sessions=fake_sessions_repo,
        users=fake_users_repo,
        user_roles=fake_user_roles_repo,
    )

    assert result.id == user.id
    assert result.name == user.name
    assert result.email == user.email
    assert len(result.session_token) > 0


async def test_success_creates_session_with_hash(
    users_in_memory: list[User],
    fake_users_repo: FakeUserRepository,
    fake_sessions_repo: FakeSessionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Сессия создана с хешем токена, не с открытым токеном."""
    user = users_in_memory[0]
    result = await authenticate_user(
        email=user.email,
        password=TEST_PASSWORD,
        sessions=fake_sessions_repo,
        users=fake_users_repo,
        user_roles=fake_user_roles_repo,
    )

    assert len(fake_sessions_repo.sessions) == 1
    session = next(iter(fake_sessions_repo.sessions.values()))

    expected_hash = hash_session_token(result.session_token)
    assert session.token_hash == expected_hash
    assert session.token_hash != result.session_token
    assert session.user_id == user.id


async def test_success_no_session_on_failure(
    users_in_memory: list[User],
    fake_users_repo: FakeUserRepository,
    fake_sessions_repo: FakeSessionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """При ошибке аутентификации сессия НЕ создаётся."""
    user = users_in_memory[0]
    with pytest.raises(AuthenticationError):
        await authenticate_user(
            email=user.email,
            password="wrong",
            sessions=fake_sessions_repo,
            users=fake_users_repo,
            user_roles=fake_user_roles_repo,
        )

    assert len(fake_sessions_repo.sessions) == 0


async def test_success_with_user_agent_and_ip(
    users_in_memory: list[User],
    fake_users_repo: FakeUserRepository,
    fake_sessions_repo: FakeSessionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """user_agent и ip_address сохраняются в сессии."""
    user = users_in_memory[0]
    await authenticate_user(
        email=user.email,
        password=TEST_PASSWORD,
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1",
        sessions=fake_sessions_repo,
        users=fake_users_repo,
        user_roles=fake_user_roles_repo,
    )

    session = next(iter(fake_sessions_repo.sessions.values()))
    assert session.user_agent == "Mozilla/5.0"
    assert session.ip_address == "127.0.0.1"


# ============================================================
# ЗАЩИТА ОТ ENUMERATION
# ============================================================


async def test_all_failures_same_message(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    fake_users_repo: FakeUserRepository,
    fake_users_repo_inactive: FakeUserRepository,
    fake_sessions_repo: FakeSessionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Все три ошибки дают одно и то же сообщение (защита от enumeration)."""
    user = users_in_memory[0]
    with pytest.raises(AuthenticationError) as exc1:
        await authenticate_user(
            email="unknown@example.com",
            password=TEST_PASSWORD,
            sessions=fake_sessions_repo,
            users=fake_users_repo,
            user_roles=fake_user_roles_repo,
        )

    with pytest.raises(AuthenticationError) as exc2:
        await authenticate_user(
            email=inactive_user_in_memory.email,
            password=TEST_PASSWORD,
            sessions=fake_sessions_repo,
            users=fake_users_repo_inactive,
            user_roles=fake_user_roles_repo,
        )

    with pytest.raises(AuthenticationError) as exc3:
        await authenticate_user(
            email=user.email,
            password="wrong",
            sessions=fake_sessions_repo,
            users=fake_users_repo,
            user_roles=fake_user_roles_repo,
        )

    assert str(exc1.value) == str(exc2.value) == str(exc3.value)
