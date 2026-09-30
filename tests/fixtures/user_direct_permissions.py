"""Fixtures for UserDirectPermission."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import PermissionCondition, User, UserDirectPermission


@pytest_asyncio.fixture
async def user_direct_permission(
    db_session: AsyncSession,
    user: User,
    permission_conditions_allow: list[PermissionCondition],
) -> UserDirectPermission:
    """Одна связь user ↔ direct condition."""
    link = UserDirectPermission(
        user_id=user.id,
        condition_id=permission_conditions_allow[0].id,
    )
    db_session.add(link)
    await db_session.flush()
    return link


@pytest_asyncio.fixture
async def user_direct_permissions(
    db_session: AsyncSession,
    user: User,
    permission_conditions_allow: list[PermissionCondition],
) -> list[UserDirectPermission]:
    """Несколько связей для одного юзера."""
    result = []
    for condition in permission_conditions_allow:
        link = UserDirectPermission(
            user_id=user.id,
            condition_id=condition.id,
        )
        db_session.add(link)
        result.append(link)
    await db_session.flush()
    return result


@pytest_asyncio.fixture
async def user_direct_permission_in_memory(
    user_in_memory: User,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> UserDirectPermission:
    """Одна связь user ↔ direct condition в памяти (no DB)."""
    return UserDirectPermission(
        user_id=user_in_memory.id,
        condition_id=permission_conditions_allow_in_memory[0].id,
    )


@pytest_asyncio.fixture
async def user_direct_permissions_in_memory(
    user_in_memory: User,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> list[UserDirectPermission]:
    """Несколько связей для одного юзера в памяти (no DB)."""
    return [
        UserDirectPermission(
            user_id=user_in_memory.id,
            condition_id=condition.id,
        )
        for condition in permission_conditions_allow_in_memory
    ]


@pytest_asyncio.fixture
async def make_user_direct_permission(db_session: AsyncSession):
    """Фабрика связей user ↔ direct condition."""

    async def _make(
        user: User,
        condition: PermissionCondition,
    ) -> UserDirectPermission:
        link = UserDirectPermission(
            user_id=user.id,
            condition_id=condition.id,
        )
        db_session.add(link)
        await db_session.flush()
        return link

    return _make
