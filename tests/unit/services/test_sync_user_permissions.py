"""Unit-тесты sync_user_permissions."""

from uuid import uuid4

from backend.app.services.sync_user_permissions import sync_user_permissions

from app.models.system import (
    PermissionCondition,
    Role,
    RolePermission,
    UserDirectPermission,
    UserPermission,
    UserRole,
)
from tests.unit.fakes.role_permission import FakeRolePermissionRepository
from tests.unit.fakes.user_direct_permission import FakeUserDirectPermissionRepository
from tests.unit.fakes.user_permission import FakeUserPermissionRepository
from tests.unit.fakes.user_role_repository import FakeUserRoleRepository

# ─────────────────────────────────────────────────────────────
# Хелперы
# ─────────────────────────────────────────────────────────────


def make_role() -> Role:
    return Role(id=uuid4(), name="Роль", owner_id=uuid4(), is_system=False, is_active=True)


def make_condition(permission_id=None) -> PermissionCondition:
    from app.models.system import ConditionType, PermissionEffect

    return PermissionCondition(
        id=uuid4(),
        permission_id=permission_id or uuid4(),
        type=ConditionType.ALL,
        effect=PermissionEffect.ALLOW,
        is_active=True,
    )


# ─────────────────────────────────────────────────────────────
# Базовые сценарии
# ─────────────────────────────────────────────────────────────


async def test_sync_no_roles_no_direct() -> None:
    """Нет ролей, нет direct → пустой набор в user_permissions."""
    user_id = uuid4()
    user_roles = FakeUserRoleRepository()
    role_permissions = FakeRolePermissionRepository()
    user_direct = FakeUserDirectPermissionRepository()
    user_perms = FakeUserPermissionRepository()

    await sync_user_permissions(
        user_id,
        user_roles=user_roles,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct,
        user_permissions=user_perms,
    )

    assert [cid for (uid, cid) in user_perms.links if uid == user_id] == []


async def test_sync_one_role_one_condition() -> None:
    """Одна роль с одной condition → одна запись."""
    user_id = uuid4()
    role = make_role()
    condition = make_condition()

    user_roles = FakeUserRoleRepository(
        links=[UserRole(user_id=user_id, role_id=role.id)],
        roles=[role],
    )
    role_permissions = FakeRolePermissionRepository(
        [RolePermission(role_id=role.id, condition_id=condition.id)]
    )
    user_direct = FakeUserDirectPermissionRepository()
    user_perms = FakeUserPermissionRepository()

    await sync_user_permissions(
        user_id,
        user_roles=user_roles,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct,
        user_permissions=user_perms,
    )

    assert [cid for (uid, cid) in user_perms.links if uid == user_id] == [condition.id]


async def test_sync_two_roles_conditions_merged() -> None:
    """Две роли → conditions объединяются."""
    user_id = uuid4()
    role_a, role_b = make_role(), make_role()
    cond_a, cond_b = make_condition(), make_condition()

    user_roles = FakeUserRoleRepository(
        links=[
            UserRole(user_id=user_id, role_id=role_a.id),
            UserRole(user_id=user_id, role_id=role_b.id),
        ],
        roles=[role_a, role_b],
    )
    role_permissions = FakeRolePermissionRepository(
        [
            RolePermission(role_id=role_a.id, condition_id=cond_a.id),
            RolePermission(role_id=role_b.id, condition_id=cond_b.id),
        ]
    )
    user_direct = FakeUserDirectPermissionRepository()
    user_perms = FakeUserPermissionRepository()

    await sync_user_permissions(
        user_id,
        user_roles=user_roles,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct,
        user_permissions=user_perms,
    )

    assert set(cid for (uid, cid) in user_perms.links if uid == user_id) == {
        cond_a.id,
        cond_b.id,
    }


async def test_sync_direct_only() -> None:
    """Только direct conditions → записываются."""
    user_id = uuid4()
    condition = make_condition()

    user_roles = FakeUserRoleRepository()
    role_permissions = FakeRolePermissionRepository()
    user_direct = FakeUserDirectPermissionRepository(
        [UserDirectPermission(user_id=user_id, condition_id=condition.id)]
    )
    user_perms = FakeUserPermissionRepository()

    await sync_user_permissions(
        user_id,
        user_roles=user_roles,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct,
        user_permissions=user_perms,
    )

    assert [cid for (uid, cid) in user_perms.links if uid == user_id] == [condition.id]


# ─────────────────────────────────────────────────────────────
# Дедупликация
# ─────────────────────────────────────────────────────────────


async def test_sync_role_and_direct_same_condition_deduplicated() -> None:
    """Одна condition из роли и direct → одна запись."""
    user_id = uuid4()
    role = make_role()
    condition = make_condition()

    user_roles = FakeUserRoleRepository(
        links=[UserRole(user_id=user_id, role_id=role.id)],
        roles=[role],
    )
    role_permissions = FakeRolePermissionRepository(
        [RolePermission(role_id=role.id, condition_id=condition.id)]
    )
    user_direct = FakeUserDirectPermissionRepository(
        [UserDirectPermission(user_id=user_id, condition_id=condition.id)]
    )
    user_perms = FakeUserPermissionRepository()

    await sync_user_permissions(
        user_id,
        user_roles=user_roles,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct,
        user_permissions=user_perms,
    )

    matched = [cid for (uid, cid) in user_perms.links if uid == user_id]
    assert matched == [condition.id]


async def test_sync_two_roles_same_condition_deduplicated() -> None:
    """Одна condition в двух ролях → одна запись."""
    user_id = uuid4()
    role_a, role_b = make_role(), make_role()
    condition = make_condition()

    user_roles = FakeUserRoleRepository(
        links=[
            UserRole(user_id=user_id, role_id=role_a.id),
            UserRole(user_id=user_id, role_id=role_b.id),
        ],
        roles=[role_a, role_b],
    )
    role_permissions = FakeRolePermissionRepository(
        [
            RolePermission(role_id=role_a.id, condition_id=condition.id),
            RolePermission(role_id=role_b.id, condition_id=condition.id),
        ]
    )
    user_direct = FakeUserDirectPermissionRepository()
    user_perms = FakeUserPermissionRepository()

    await sync_user_permissions(
        user_id,
        user_roles=user_roles,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct,
        user_permissions=user_perms,
    )

    matched = [cid for (uid, cid) in user_perms.links if uid == user_id]
    assert matched == [condition.id]


# ─────────────────────────────────────────────────────────────
# Замена (replace_for_user)
# ─────────────────────────────────────────────────────────────


async def test_sync_replaces_old_links() -> None:
    """Старые связи удаляются, новые добавляются."""
    user_id = uuid4()
    old_condition = make_condition()
    new_condition = make_condition()
    role = make_role()

    user_roles = FakeUserRoleRepository(
        links=[UserRole(user_id=user_id, role_id=role.id)],
        roles=[role],
    )
    role_permissions = FakeRolePermissionRepository(
        [RolePermission(role_id=role.id, condition_id=new_condition.id)]
    )
    user_direct = FakeUserDirectPermissionRepository()
    user_perms = FakeUserPermissionRepository()
    user_perms.add(UserPermission(user_id=user_id, condition_id=old_condition.id))

    await sync_user_permissions(
        user_id,
        user_roles=user_roles,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct,
        user_permissions=user_perms,
    )

    matched = [cid for (uid, cid) in user_perms.links if uid == user_id]
    assert matched == [new_condition.id]
    assert old_condition.id not in matched


# ─────────────────────────────────────────────────────────────
# Изоляция по user_id
# ─────────────────────────────────────────────────────────────


async def test_sync_does_not_touch_other_users() -> None:
    """Связи другого юзера не трогаются."""
    user_id = uuid4()
    other_user_id = uuid4()
    other_condition = make_condition()
    role = make_role()
    condition = make_condition()

    user_roles = FakeUserRoleRepository(
        links=[UserRole(user_id=user_id, role_id=role.id)],
        roles=[role],
    )
    role_permissions = FakeRolePermissionRepository(
        [RolePermission(role_id=role.id, condition_id=condition.id)]
    )
    user_direct = FakeUserDirectPermissionRepository()
    user_perms = FakeUserPermissionRepository()
    user_perms.add(UserPermission(user_id=other_user_id, condition_id=other_condition.id))

    await sync_user_permissions(
        user_id,
        user_roles=user_roles,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct,
        user_permissions=user_perms,
    )

    other = [cid for (uid, cid) in user_perms.links if uid == other_user_id]
    assert other == [other_condition.id]


# ─────────────────────────────────────────────────────────────
# Активность ролей
# ─────────────────────────────────────────────────────────────


async def test_sync_skips_inactive_roles() -> None:
    """Неактивная роль не даёт conditions (BR-ROLE-023)."""
    user_id = uuid4()
    active_role = make_role()
    inactive_role = make_role()
    inactive_role.is_active = False
    cond_active = make_condition()
    cond_inactive = make_condition()

    user_roles = FakeUserRoleRepository(
        links=[
            UserRole(user_id=user_id, role_id=active_role.id),
            UserRole(user_id=user_id, role_id=inactive_role.id),
        ],
        roles=[inactive_role, active_role],
    )
    role_permissions = FakeRolePermissionRepository(
        [
            RolePermission(role_id=active_role.id, condition_id=cond_active.id),
            RolePermission(role_id=inactive_role.id, condition_id=cond_inactive.id),
        ]
    )
    user_direct = FakeUserDirectPermissionRepository()
    user_perms = FakeUserPermissionRepository()

    await sync_user_permissions(
        user_id,
        user_roles=user_roles,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct,
        user_permissions=user_perms,
    )

    matched = set(cid for (uid, cid) in user_perms.links if uid == user_id)
    assert matched == {cond_active.id}
    assert cond_inactive.id not in matched
