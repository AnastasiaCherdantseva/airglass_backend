"""
Фикстуры пользователей.
"""

from datetime import UTC, datetime, timedelta
from itertools import count
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
async def user_admin(
    user: User,
    user_system_role: UserRole,
    system_role_permissions: list[RolePermission],
    user_permissions: list[UserPermission],
) -> User:

    return user


@pytest_asyncio.fixture
async def children_user_admin(user_admin: User, make_user) -> list[User]:
    """
    Five direct children of user_admin in the DB (created_at ascending).

    Пять прямых детей user_admin в БД (created_at по возрастанию).
    """
    base = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        await make_user(
            email=f"child{i}@example.com",
            parent_id=user_admin.id,
            created_at=base + timedelta(minutes=i),
        )
        for i in range(5)
    ]


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
async def user_admin_in_memory(users_in_memory: list[User]) -> User:
    """
    Actor for tests of children listing: users_in_memory[0].

    Актор для тестов списка детей: users_in_memory[0].
    """
    return users_in_memory[0]


@pytest_asyncio.fixture
async def children_user_admin_in_memory(
    user_admin_in_memory: User, make_user_in_memory
) -> list[User]:
    """
    Five direct children of parent_in_memory (in memory, ascending created_at).

    Пять прямых детей parent_in_memory (в памяти, created_at по возрастанию).
    """
    return [
        make_user_in_memory(email=f"child{i}@example.com", parent_id=user_admin_in_memory.id)
        for i in range(5)
    ]


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
        created_at: datetime | None = None,
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
        if created_at is not None:
            user.created_at = created_at
        db_session.add(user)
        await db_session.flush()
        return user

    return _make


@pytest_asyncio.fixture
async def make_user_in_memory():
    """
    Factory of in-memory users (no DB). created_at grows with each call,
    so the order in paginated results is deterministic.

    Фабрика пользователей в памяти (без БД). created_at растёт с каждым
    вызовом, поэтому порядок в пагинации стабилен.
    """
    counter = count()
    base = datetime(2026, 1, 1, tzinfo=UTC)

    def _make(
        *,
        email: str,
        name: str = "Тестовый",
        parent_id: UUID | None = None,
        is_active: bool = True,
        deleted_at: datetime | None = None,
    ) -> User:
        return User(
            id=uuid4(),
            email=email,
            name=name,
            parent_id=parent_id,
            password_hash=get_test_password_hash(),
            is_active=is_active,
            email_verified=datetime.now(),
            deleted_at=deleted_at,
            created_at=base + timedelta(minutes=next(counter)),
        )

    return _make
