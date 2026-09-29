"""
Фикстуры пользователей.
"""

from uuid import uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.system import User

_PASSWORD_HASH_CACHE: str | None = None

TEST_PASSWORD = "secretsecretsecret"


def get_test_password_hash() -> str:
    """Return cached bcrypt hash for tests."""
    global _PASSWORD_HASH_CACHE
    if _PASSWORD_HASH_CACHE is None:
        _PASSWORD_HASH_CACHE = hash_password(TEST_PASSWORD)
    return _PASSWORD_HASH_CACHE


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    """Ready-to-use active user in the database."""
    user = User(
        id=uuid4(),
        name="Аня",
        email="anya@example.com",
        password_hash=get_test_password_hash(),
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    """Ready-to-use inactive user in the database."""
    user = User(
        id=uuid4(),
        name="Иван",
        email="ivan@example.com",
        password_hash=get_test_password_hash(),
        is_active=False,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def users(db_session: AsyncSession) -> list[User]:
    """Несколько пользователей для тестов пагинации."""
    users = [
        User(
            id=uuid4(),
            name=f"User{i}",
            email=f"user{i}@example.com",
            password_hash=get_test_password_hash(),
            is_active=True,
        )
        for i in range(5)
    ]
    db_session.add_all(users)
    await db_session.flush()
    return users


@pytest_asyncio.fixture
async def user_in_memory() -> User:
    """Ready-to-use active user in memory (no DB)."""
    return User(
        id=uuid4(),
        name="Аня",
        email="anya@example.com",
        password_hash=get_test_password_hash(),
        is_active=True,
    )


@pytest_asyncio.fixture
async def inactive_user_in_memory() -> User:
    """Ready-to-use inactive user in memory (no DB)."""
    return User(
        id=uuid4(),
        name="Иван",
        email="ivan@example.com",
        password_hash=get_test_password_hash(),
        is_active=False,
    )


@pytest_asyncio.fixture
async def users_in_memory() -> list[User]:
    """Several active users in memory (no DB)."""
    return [
        User(
            id=uuid4(),
            name=f"User{i}",
            email=f"user{i}@example.com",
            password_hash=get_test_password_hash(),
            is_active=True,
        )
        for i in range(5)
    ]
