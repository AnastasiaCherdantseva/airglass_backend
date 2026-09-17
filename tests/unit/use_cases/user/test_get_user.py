"""
get user use-case test.

"""

from uuid import uuid4

import pytest

from app.core.exceptions import NotFoundError
from app.models.system import User
from app.use_cases.user.get_user import get_user
from tests.unit.fakes.user_repository import FakeUserRepository


async def test_get_user_success(users_in_memory: list[User]) -> None:
    """Return an existing user by ID."""
    fake_user_repo = FakeUserRepository(users_in_memory)
    user_id = next(iter(fake_user_repo.users))
    expected = fake_user_repo.users[user_id]

    result = await get_user(user_id, users=fake_user_repo)

    assert result.id == expected.id
    assert result.email == expected.email
    assert result.name == expected.name
    assert result.is_active == expected.is_active


async def test_get_user_not_found(users_in_memory: list[User]) -> None:
    """Raise NotFoundError if the user not found"""
    fake_user_repo = FakeUserRepository(users_in_memory)

    with pytest.raises(NotFoundError):
        await get_user(uuid4(), users=fake_user_repo)


async def test_get_user_inactive(
    inactive_user_in_memory: User,
) -> None:
    """get_user returns an inactive user by ID."""
    repo = FakeUserRepository([inactive_user_in_memory])

    result = await get_user(inactive_user_in_memory.id, users=repo)

    assert result.id == inactive_user_in_memory.id
    assert result.is_active is False
