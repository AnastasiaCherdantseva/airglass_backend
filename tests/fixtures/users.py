"""
Фикстуры пользователей.
"""

from datetime import datetime
from uuid import UUID, uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.dto.system.user import UserCreateFull
from app.models.system import User
from app.models.system.role import Role
from app.models.system.role_permission import RolePermission
from app.models.system.user_permission import UserPermission
from app.models.system.user_role import UserRole
from app.schemas.system.user import UserCreateRequest

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
        email_verified=datetime.now(),
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
            email_verified=datetime.now(),
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
        email_verified=datetime.now(),
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
            email_verified=datetime.now(),
        )
        for i in range(5)
    ]


@pytest_asyncio.fixture
async def new_user_data(user: User) -> UserCreateFull:
    """Several active users in memory (no DB)."""

    password_hash = hash_password(TEST_PASSWORD)
    return UserCreateFull(
        email="new@example.com",
        name="Name",
        parent_id=user.id,
        password_hash=password_hash,
        is_active=True,
    )


@pytest_asyncio.fixture
async def new_user_data_request(role: Role) -> UserCreateRequest:
    """Several active users in memory (no DB)."""

    return {
        "email": "new@example.com",
        "name": "Новый",
        "password": TEST_PASSWORD,
        "role_ids": [str(role.id)],
    }


@pytest_asyncio.fixture
async def make_user(db_session: AsyncSession):
    """Фабрика пользователей."""

    async def _make(
        *,
        email: str,
        name: str = "Тестовый",
        parent_id: UUID | None = None,
        is_active: bool = True,
        email_verified: datetime | None = None,
        deleted_at: datetime | None = None,
    ) -> User:
        user = User(
            id=uuid4(),
            email=email,
            name=name,
            parent_id=parent_id,
            password_hash=get_test_password_hash(),
            is_active=is_active,
            email_verified=email_verified,
            deleted_at=deleted_at,
        )
        db_session.add(user)
        await db_session.flush()
        return user

    return _make


@pytest_asyncio.fixture
async def user_admin(
    user: User,
    user_system_role: UserRole,
    system_role_permissions: list[RolePermission],
    user_permissions: list[UserPermission],
) -> User:

    return user
