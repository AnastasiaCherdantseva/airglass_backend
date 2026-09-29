"""Fixtures for Role."""

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
