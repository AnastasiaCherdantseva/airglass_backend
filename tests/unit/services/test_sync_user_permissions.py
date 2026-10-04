"""Unit-тесты sync_user_permissions."""

from uuid import uuid4

import pytest

from app.core.exceptions import NotFoundError
from app.models.system import (
    Role,
    UserDirectPermission,
)
from app.models.system.permission_condition import PermissionCondition
from app.models.system.user import User
from app.models.system.user_role import UserRole
from app.services.sync_user_permissions import sync_user_permissions
from tests.unit.fakes.role_permission import FakeRolePermissionRepository
from tests.unit.fakes.user_direct_permission import FakeUserDirectPermissionRepository
from tests.unit.fakes.user_permission import FakeUserPermissionRepository
from tests.unit.fakes.user_role_repository import FakeUserRoleRepository

# ─────────────────────────────────────────────────────────────
# Базовые сценарии
# ─────────────────────────────────────────────────────────────


# users_in_memory: list[User],
#     inactive_user_in_memory: User,
#     role_in_memory: Role,
#     fake_users_repo: FakeUserRepository,
#     fake_user_roles_repo: FakeUserRoleRepository,
#     fake_role_permissions_repo: FakeRolePermissionRepository,
#     fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
#     fake_user_permissions_repo: FakeUserPermissionRepository,
#     fake_roles_repo: FakeRoleRepository,
async def test_sync_no_roles_no_direct(
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Нет ролей, нет direct → ошибка NotFoundError → пустой набор в user_permissions."""
    user_id = uuid4()
    with pytest.raises(NotFoundError):
        await sync_user_permissions(
            user_id,
            user_roles=fake_user_roles_repo,
            role_permissions=fake_role_permissions_repo,
            user_direct_permissions=fake_user_direct_permissions_repo,
            user_permissions=fake_user_permissions_repo,
        )

    assert [cid for (uid, cid) in fake_user_permissions_repo.links if uid == user_id] == []


async def test_sync_one_role(
    users_in_memory: list[User],
    role_in_memory: Role,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Одна роль  → все ее права."""
    user = users_in_memory[1]
    await sync_user_permissions(
        user.id,
        user_roles=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
    )
    cnd = await fake_role_permissions_repo.get_condition_ids_by_role_id(role_in_memory.id)
    assert [
        cid for (rid, cid) in fake_role_permissions_repo.links if rid == role_in_memory.id
    ] == cnd
    assert [cid for (uid, cid) in fake_user_permissions_repo.links if uid == user.id] == cnd


async def test_sync_direct_only(
    users_in_memory: list[User],
    role_in_memory: Role,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> None:
    """Только direct conditions → записываются."""

    user = users_in_memory[1]
    cnd = permission_conditions_allow_in_memory[0]
    fake_user_direct_permissions_repo.links[(user.id, cnd.id)] = UserDirectPermission(
        user_id=user.id, condition_id=cnd.id
    )
    await sync_user_permissions(
        user.id,
        user_roles=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
    )
    cnd_base = await fake_role_permissions_repo.get_condition_ids_by_role_id(role_in_memory.id)
    assert [cid for (uid, cid) in fake_user_permissions_repo.links if uid == user.id] == list(
        set([cnd.id] + cnd_base)
    )


# ─────────────────────────────────────────────────────────────
# Дедупликация
# ─────────────────────────────────────────────────────────────


async def test_sync_role_and_direct_condition_deduplicated(
    users_in_memory: list[User],
    system_role_in_memory: Role,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> None:
    """condition из роли и direct → cхлопываются."""
    user = users_in_memory[0]
    cnd = permission_conditions_allow_in_memory[0]
    fake_user_direct_permissions_repo.links[(user.id, cnd.id)] = UserDirectPermission(
        user_id=user.id, condition_id=cnd.id
    )
    await sync_user_permissions(
        user.id,
        user_roles=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
    )
    cnd_system = await fake_role_permissions_repo.get_condition_ids_by_role_id(
        system_role_in_memory.id
    )
    matched = [cid for (uid, cid) in fake_user_permissions_repo.links if uid == user.id]
    assert sorted(matched) == sorted(cnd_system)


async def test_sync_two_roles_conditions_merged(
    users_in_memory: list[User],
    system_role_in_memory: Role,
    role_in_memory: Role,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Две роли → conditions cхлопываются."""
    user = users_in_memory[0]
    await sync_user_permissions(
        user.id,
        user_roles=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
    )
    cnd_system = await fake_role_permissions_repo.get_condition_ids_by_role_id(
        system_role_in_memory.id
    )
    cnd_base = await fake_role_permissions_repo.get_condition_ids_by_role_id(role_in_memory.id)

    assert [
        cid for (rid, cid) in fake_role_permissions_repo.links if rid == system_role_in_memory.id
    ] == cnd_system
    assert [
        cid for (rid, cid) in fake_role_permissions_repo.links if rid == role_in_memory.id
    ] == cnd_base
    # Системная роль уже содержит права из базовой
    cids = [cid for (uid, cid) in fake_user_permissions_repo.links if uid == user.id]
    assert set(cids) == set(cnd_system)


# # ─────────────────────────────────────────────────────────────
# # Замена (replace_for_user)
# # ─────────────────────────────────────────────────────────────


async def test_sync_replaces_old_links(
    users_in_memory: list[User],
    system_role_in_memory: Role,
    role_in_memory: Role,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> None:
    """Старые связи удаляются, новые добавляются."""
    user = users_in_memory[0]

    del fake_user_roles_repo.links[(user.id, system_role_in_memory.id)]
    fake_user_roles_repo.links[(user.id, role_in_memory.id)] = UserRole(
        user_id=user.id, role_id=role_in_memory.id
    )
    await sync_user_permissions(
        user.id,
        user_roles=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
    )
    cnd_base = await fake_role_permissions_repo.get_condition_ids_by_role_id(role_in_memory.id)
    matched = [cid for (uid, cid) in fake_user_permissions_repo.links if uid == user.id]
    assert sorted(matched) == sorted(cnd_base)


# # ─────────────────────────────────────────────────────────────
# # Изоляция по user_id
# # ─────────────────────────────────────────────────────────────


async def test_sync_does_not_touch_other_users(
    users_in_memory: list[User],
    system_role_in_memory: Role,
    role_in_memory: Role,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> None:
    """Связи другого юзера не трогаются."""
    user = users_in_memory[0]
    another_user = users_in_memory[1]
    another_cnd = [cid for (uid, cid) in fake_user_permissions_repo.links if uid == another_user.id]

    del fake_user_roles_repo.links[(user.id, system_role_in_memory.id)]
    fake_user_roles_repo.links[(user.id, role_in_memory.id)] = UserRole(
        user_id=user.id, role_id=role_in_memory.id
    )
    await sync_user_permissions(
        user.id,
        user_roles=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
    )
    cnd_base = await fake_role_permissions_repo.get_condition_ids_by_role_id(role_in_memory.id)
    another_cnd_after = [
        cid for (uid, cid) in fake_user_permissions_repo.links if uid == another_user.id
    ]
    matched = [cid for (uid, cid) in fake_user_permissions_repo.links if uid == user.id]
    assert sorted(matched) == sorted(cnd_base)
    assert sorted(another_cnd_after) == sorted(another_cnd)


# # ─────────────────────────────────────────────────────────────
# # Активность ролей
# # ─────────────────────────────────────────────────────────────


async def test_sync_skips_inactive_roles(
    users_in_memory: list[User],
    role_in_memory: Role,
    inactive_role_in_memory: Role,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> None:
    """Неактивная роль не даёт conditions (BR-ROLE-023)."""
    user = users_in_memory[1]

    fake_user_roles_repo.links[(user.id, inactive_role_in_memory.id)] = UserRole(
        user_id=user.id, role_id=inactive_role_in_memory.id
    )
    inactive_role_cnd = [
        cid for (rid, cid) in fake_role_permissions_repo.links if rid == inactive_role_in_memory.id
    ]
    base_role_cnd = [
        cid for (rid, cid) in fake_role_permissions_repo.links if rid == role_in_memory.id
    ]
    await sync_user_permissions(
        user.id,
        user_roles=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
    )
    matched_after = [cid for (uid, cid) in fake_user_permissions_repo.links if uid == user.id]
    for m in inactive_role_cnd:
        assert m not in matched_after
    for m in base_role_cnd:
        assert m in matched_after
