import pytest

from app.core.exceptions import PermissionDeniedError
from app.models.system import User
from app.use_cases.user.authenticate_user import authenticate_user
from tests.unit.fakes.user_repository import FakeUserRepository


async def test_authenticate_user_success(users_in_memory: list[User]) -> None:
    """Return user model object if password matches"""
    fake_user_repo = FakeUserRepository(users_in_memory)

    result = await authenticate_user(users_in_memory[0].email, "secret", users=fake_user_repo)

    assert result.id == users_in_memory[0].id
    assert result.email == users_in_memory[0].email
    assert result.name == users_in_memory[0].name
    assert result.is_active == users_in_memory[0].is_active
    assert result.password_hash == users_in_memory[0].password_hash


async def test_authenticate_user_wrong_password(users_in_memory: list[User]) -> None:
    """Raise PermissionDeniedError if password does not match"""
    fake_user_repo = FakeUserRepository(users_in_memory)

    with pytest.raises(PermissionDeniedError):
        await authenticate_user(users_in_memory[0].email, "another_password", users=fake_user_repo)


async def test_authenticate_user_unknown_email(
    users_in_memory: list[User],
) -> None:
    """Raise PermissionDeniedError when the email is unknown."""
    fake_user_repo = FakeUserRepository(users_in_memory)

    with pytest.raises(PermissionDeniedError):
        await authenticate_user(
            "nobody@example.com",
            "any",
            users=fake_user_repo,
        )


async def test_authenticate_user_inactive(
    inactive_user_in_memory: User,
) -> None:
    """Raise PermissionDeniedError for an inactive user."""
    repo = FakeUserRepository([inactive_user_in_memory])

    with pytest.raises(PermissionDeniedError):
        await authenticate_user(
            inactive_user_in_memory.email,
            "secret",
            users=repo,
        )
