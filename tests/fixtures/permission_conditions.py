from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import ConditionType, Permission, PermissionCondition, PermissionEffect
from app.models.system.role import Role


@pytest_asyncio.fixture
async def permission_conditions_allow(
    db_session: AsyncSession,
    permissions: list[Permission],
    role: Role,
    system_role: Role,
    inactive_role: Role,
) -> list[PermissionCondition]:
    result = []
    for p in permissions:
        if p.resource == "users" and p.action == "create":
            r1 = PermissionCondition(
                permission_id=p.id,
                effect=PermissionEffect.ALLOW,
                type=ConditionType.ROLE,
                role_id=role.id,
                is_active=True,
            )
            r2 = PermissionCondition(
                permission_id=p.id,
                effect=PermissionEffect.ALLOW,
                type=ConditionType.ROLE,
                role_id=inactive_role.id,
                is_active=True,
            )
            r3 = PermissionCondition(
                permission_id=p.id,
                effect=PermissionEffect.ALLOW,
                type=ConditionType.ROLE,
                role_id=system_role.id,
                is_active=True,
            )
            db_session.add_all([r1, r2, r3])
            result += [r1, r2, r3]
            continue
        new = PermissionCondition(
            permission_id=p.id,
            effect=PermissionEffect.ALLOW,
            type=ConditionType.SUBTREE,
            is_active=True,
        )
        db_session.add(new)
        result.append(new)
    await db_session.flush()
    return result


@pytest_asyncio.fixture
async def permission_conditions_deny(
    db_session: AsyncSession, permissions: list[Permission]
) -> list[PermissionCondition]:
    result = []
    for p in permissions:
        new = PermissionCondition(
            permission_id=p.id, effect=PermissionEffect.DENY, type=ConditionType.ALL, is_active=True
        )
        db_session.add(new)
        result.append(new)
    await db_session.flush()
    return result


@pytest_asyncio.fixture
async def permission_conditions_allow_in_memory(
    permissions_in_memory: list[Permission],
) -> list[PermissionCondition]:
    """ALLOW-условия для всех permissions в памяти (no DB)."""
    return [
        PermissionCondition(
            id=uuid4(),
            permission_id=p.id,
            effect=PermissionEffect.ALLOW,
            type=ConditionType.SUBTREE,
            is_active=True,
        )
        for p in permissions_in_memory
    ]


@pytest_asyncio.fixture
async def permission_conditions_deny_in_memory(
    permissions_in_memory: list[Permission],
) -> list[PermissionCondition]:
    """DENY-условия для всех permissions в памяти (no DB)."""
    return [
        PermissionCondition(
            id=uuid4(),
            permission_id=p.id,
            effect=PermissionEffect.DENY,
            type=ConditionType.ALL,
            is_active=True,
        )
        for p in permissions_in_memory
    ]


@pytest_asyncio.fixture
async def make_condition(db_session: AsyncSession):
    async def _make(
        permission: Permission,
        *,
        type_: ConditionType,
        effect: PermissionEffect = PermissionEffect.ALLOW,
        is_active: bool = True,
        role_id: UUID | None = None,
        category_id: UUID | None = None,
        media_type_id: UUID | None = None,
    ) -> PermissionCondition:
        condition = PermissionCondition(
            permission_id=permission.id,
            type=type_,
            effect=effect,
            is_active=is_active,
            role_id=role_id,
            category_id=category_id,
            media_type_id=media_type_id,
        )
        db_session.add(condition)
        await db_session.flush()
        return condition

    return _make


@pytest.fixture
def make_condition_in_memory():
    def _make(
        permission: Permission,
        *,
        type_: ConditionType,
        effect: PermissionEffect = PermissionEffect.ALLOW,
        is_active: bool = True,
        role_id: UUID | None = None,
        category_id: UUID | None = None,
        media_type_id: UUID | None = None,
    ) -> PermissionCondition:
        condition = PermissionCondition(
            id=uuid4(),
            permission_id=permission.id,
            type=type_,
            effect=effect,
            is_active=is_active,
            role_id=role_id,
            category_id=category_id,
            media_type_id=media_type_id,
        )
        return condition

    return _make
