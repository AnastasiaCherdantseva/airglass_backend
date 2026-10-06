"""Fixtures for RolePermission."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import PermissionCondition, Role, RolePermission


@pytest_asyncio.fixture
async def role_permission(
    db_session: AsyncSession,
    role: Role,
    permission_conditions_allow: list[PermissionCondition],
) -> RolePermission:
    """Одна связь role ↔ condition."""
    for p in permission_conditions_allow:
        if p.role_id == role.id:
            link = RolePermission(
                role_id=role.id,
                condition_id=p.id,
            )
            db_session.add(link)
            await db_session.flush()
            return link


@pytest_asyncio.fixture
async def system_role_permissions(
    db_session: AsyncSession,
    system_role: Role,
    permission_conditions_allow: list[PermissionCondition],
) -> list[RolePermission]:
    """Несколько связей для одной роли."""
    result = []
    for condition in permission_conditions_allow:
        link = RolePermission(
            role_id=system_role.id,
            condition_id=condition.id,
        )
        db_session.add(link)
        result.append(link)
    await db_session.flush()
    return result


@pytest_asyncio.fixture
async def role_permission_in_memory(
    role_in_memory: Role,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> RolePermission:
    """Одна связь role ↔ condition в памяти (no DB)."""
    return RolePermission(
        role_id=role_in_memory.id,
        condition_id=permission_conditions_allow_in_memory[0].id,
    )


@pytest_asyncio.fixture
async def role_permissions_in_memory(
    system_role_in_memory: Role,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> list[RolePermission]:
    """Несколько связей для одной роли в памяти (no DB)."""
    return [
        RolePermission(
            role_id=system_role_in_memory.id,
            condition_id=condition.id,
        )
        for condition in permission_conditions_allow_in_memory
    ]


@pytest_asyncio.fixture
async def make_role_permission(db_session: AsyncSession):
    """Фабрика связей role ↔ condition."""

    async def _make(role: Role, condition: PermissionCondition) -> RolePermission:
        link = RolePermission(
            role_id=role.id,
            condition_id=condition.id,
        )
        db_session.add(link)
        await db_session.flush()
        return link

    return _make
