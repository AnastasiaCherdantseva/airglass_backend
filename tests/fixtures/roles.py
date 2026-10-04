"""Fixtures for Role."""

from uuid import uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import Role, User


@pytest_asyncio.fixture
async def role(db_session: AsyncSession, user: User) -> Role:
    """Готовая пользовательская роль в БД (owner = user)."""
    role = Role(
        name="Тестовая роль",
        owner_id=user.id,
        description="Для тестов",
        is_system=False,
        is_active=True,
    )
    db_session.add(role)
    await db_session.flush()
    return role


@pytest_asyncio.fixture
async def system_role(db_session: AsyncSession) -> Role:
    """Готовая системная роль в БД (owner_id = None)."""
    role = Role(
        name="Системная роль",
        owner_id=None,
        description="Системная",
        is_system=True,
        is_active=True,
    )
    db_session.add(role)
    await db_session.flush()
    return role


@pytest_asyncio.fixture
async def system_roles(db_session: AsyncSession) -> list[Role]:
    """Несколько системных ролей в БД (owner_id = None)."""
    roles = []
    for i in range(3):
        role = Role(
            name=f"Системная Роль {i}",
            owner_id=None,
            description="Системная",
            is_system=True,
            is_active=True,
        )
        db_session.add(role)
        roles.append(role)
    await db_session.flush()
    return roles


@pytest_asyncio.fixture
async def roles(db_session: AsyncSession, user: User) -> list[Role]:
    """Несколько пользовательских ролей для одного владельца."""
    result = []
    for i in range(3):
        r = Role(
            name=f"Роль {i}",
            owner_id=user.id,
            description=f"Описание {i}",
            is_system=False,
            is_active=True,
        )
        db_session.add(r)
        result.append(r)
    await db_session.flush()
    return result


@pytest_asyncio.fixture
async def roles_for_two_users(
    db_session: AsyncSession,
    users: list[User],
) -> dict:
    """Роли двух разных владельцев (для тестов изоляции)."""
    user_a, user_b = users[0], users[1]
    roles_a = [
        Role(
            name=f"A role {i}",
            owner_id=user_a.id,
            description=None,
            is_system=False,
            is_active=True,
        )
        for i in range(2)
    ]
    roles_b = [
        Role(
            name=f"B role {i}",
            owner_id=user_b.id,
            description=None,
            is_system=False,
            is_active=True,
        )
        for i in range(3)
    ]
    db_session.add_all(roles_a + roles_b)
    await db_session.flush()
    return {
        user_a.id: [r.id for r in roles_a],
        user_b.id: [r.id for r in roles_b],
    }


@pytest_asyncio.fixture
async def role_in_memory(user_in_memory: User) -> Role:
    """Готовая пользовательская роль в памяти (no DB)."""
    return Role(
        id=uuid4(),
        name="Тестовая роль",
        owner_id=user_in_memory.id,
        description="Для тестов",
        is_system=False,
        is_active=True,
    )


@pytest_asyncio.fixture
async def system_role_in_memory() -> Role:
    """Готовая системная роль в памяти (no DB)."""
    return Role(
        id=uuid4(),
        name="Системная роль",
        owner_id=None,
        description="Системная",
        is_system=True,
        is_active=True,
    )


@pytest_asyncio.fixture
async def system_roles_in_memory() -> list[Role]:
    """Несколько системных ролей в памяти (no DB)."""
    return [
        Role(
            id=uuid4(),
            name=f"Системная Роль {i}",
            owner_id=None,
            description="Системная",
            is_system=True,
            is_active=True,
        )
        for i in range(3)
    ]


@pytest_asyncio.fixture
async def inactive_role_in_memory() -> Role:
    return Role(
        id=uuid4(),
        name="Неактивная Роль",
        owner_id=None,
        description="Неактивная Роль",
        is_system=True,
        is_active=False,
    )


@pytest_asyncio.fixture
async def roles_in_memory(user_in_memory: User) -> list[Role]:
    """Несколько пользовательских ролей в памяти (no DB)."""
    return [
        Role(
            id=uuid4(),
            name=f"Роль {i}",
            owner_id=user_in_memory.id,
            description=f"Описание {i}",
            is_system=False,
            is_active=True,
        )
        for i in range(3)
    ]


@pytest_asyncio.fixture
async def make_role(db_session: AsyncSession):
    """Фабрика ролей."""

    async def _make(
        *,
        name: str,
        owner_id=None,
        description: str | None = None,
        is_system: bool = False,
        is_active: bool = True,
    ) -> Role:
        role = Role(
            name=name,
            owner_id=owner_id,
            description=description,
            is_system=is_system,
            is_active=is_active,
        )
        db_session.add(role)
        await db_session.flush()
        return role

    return _make
