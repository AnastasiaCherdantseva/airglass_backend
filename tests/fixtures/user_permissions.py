"""Fixtures for UserPermission."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import PermissionCondition, User, UserPermission


@pytest_asyncio.fixture
async def user_permission(
    db_session: AsyncSession,
    user: User,
    permission_conditions_allow: list[PermissionCondition],
) -> UserPermission:
    """Одна связь user ↔ condition."""
    link = UserPermission(
        user_id=user.id,
        condition_id=permission_conditions_allow[0].id,
    )
    db_session.add(link)
    await db_session.flush()
    return link


@pytest_asyncio.fixture
async def user_permissions(
    db_session: AsyncSession,
    user: User,
    permission_conditions_allow: list[PermissionCondition],
) -> list[UserPermission]:
    """Несколько связей для одного юзера (по одной на каждую condition)."""
    result = []
    for condition in permission_conditions_allow:
        link = UserPermission(
            user_id=user.id,
            condition_id=condition.id,
        )
        db_session.add(link)
        result.append(link)
    await db_session.flush()
    return result


@pytest_asyncio.fixture
async def make_user_permission(db_session: AsyncSession):
    """Фабрика связей user ↔ condition."""

    async def _make(
        user: User,
        condition: PermissionCondition,
    ) -> UserPermission:
        link = UserPermission(
            user_id=user.id,
            condition_id=condition.id,
        )
        db_session.add(link)
        await db_session.flush()
        return link

    return _make
