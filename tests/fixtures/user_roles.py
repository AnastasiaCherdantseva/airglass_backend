"""Fixtures for UserRole."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import Role, User, UserRole


@pytest_asyncio.fixture
async def user_system_role(
    db_session: AsyncSession,
    user: User,
    system_role: Role,
) -> UserRole:
    """Одна связь user ↔ системная role."""
    link = UserRole(user_id=user.id, role_id=system_role.id)
    db_session.add(link)
    await db_session.flush()
    return link


@pytest_asyncio.fixture
async def user_default_role(
    db_session: AsyncSession,
    user: User,
    role: Role,
) -> UserRole:
    """Одна связь user ↔ role."""
    link = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(link)
    await db_session.flush()
    return link


@pytest_asyncio.fixture
async def user_roles(
    db_session: AsyncSession,
    user: User,
    system_roles: list[Role],
) -> list[UserRole]:
    """Несколько связей для одного юзера."""
    result = []
    for role in system_roles:
        link = UserRole(user_id=user.id, role_id=role.id)
        db_session.add(link)
        result.append(link)
    await db_session.flush()
    return result


@pytest_asyncio.fixture
async def user_role_in_memory(user_in_memory: User, system_role_in_memory: Role) -> UserRole:
    """Одна связь user ↔ role в памяти (no DB)."""
    return UserRole(user_id=user_in_memory.id, role_id=system_role_in_memory.id)


@pytest_asyncio.fixture
async def user_roles_in_memory(
    user_in_memory: User,
    system_roles_in_memory: list[Role],
) -> list[UserRole]:
    """Несколько связей для одного юзера в памяти (no DB)."""
    return [UserRole(user_id=user_in_memory.id, role_id=role.id) for role in system_roles_in_memory]


@pytest_asyncio.fixture
async def make_user_role(db_session: AsyncSession):
    """Фабрика связей user ↔ role."""

    async def _make(user: User, role: Role) -> UserRole:
        link = UserRole(user_id=user.id, role_id=role.id)
        db_session.add(link)
        await db_session.flush()
        return link

    return _make
