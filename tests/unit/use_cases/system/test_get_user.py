"""
get user use-case test.

"""

from uuid import uuid4

import pytest

from app.core.exceptions import NotFoundError
from app.models.system import User
from app.use_cases.system.get_user import get_user
from tests.unit.fakes.user_repository import FakeUserRepository


async def test_get_user_success(fake_users_repo: FakeUserRepository) -> None:
    """Return an existing user by ID."""
    user_id = next(iter(fake_users_repo.users))
    expected = fake_users_repo.users[user_id]

    result = await get_user(user_id, users=fake_users_repo)

    assert result.id == expected.id
    assert result.email == expected.email
    assert result.name == expected.name
    assert result.is_active == expected.is_active


async def test_get_user_not_found(fake_users_repo: FakeUserRepository) -> None:
    """Raise NotFoundError if the user not found"""
    with pytest.raises(NotFoundError):
        await get_user(uuid4(), users=fake_users_repo)


async def test_get_user_inactive(
    inactive_user_in_memory: User, fake_users_repo_inactive: FakeUserRepository
) -> None:
    """get_user returns an inactive user by ID."""

    result = await get_user(inactive_user_in_memory.id, users=fake_users_repo_inactive)

    assert result.id == inactive_user_in_memory.id
    assert result.is_active is False
