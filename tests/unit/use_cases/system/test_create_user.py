"""
Unit tests for the create_user use case (fake repositories, no DB).

Юнит-тесты юзкейса create_user (фейковые репозитории, без БД).
"""

from uuid import UUID

import pytest

from app.core.exceptions import ConflictError, PermissionDeniedError, ValidationError
from app.core.security import is_verified_password
from app.dto import (
    CurrentUser,
    GroupedPermission,
    UserCreate,
    UserWithRolesOutput,
)
from app.models.system import (
    Role,
    User,
)
from app.use_cases.system.create_user import create_user
from tests.unit.fakes.role import FakeRoleRepository
from tests.unit.fakes.role_permission import FakeRolePermissionRepository
from tests.unit.fakes.user_direct_permission import FakeUserDirectPermissionRepository
from tests.unit.fakes.user_permission import FakeUserPermissionRepository
from tests.unit.fakes.user_repository import FakeUserRepository
from tests.unit.fakes.user_role_repository import FakeUserRoleRepository

PASSWORD = "secretsecretsecret"


def make_actor(user: User, permission_group: list[GroupedPermission]) -> CurrentUser:
    return CurrentUser(
        id=user.id,
        email=user.email,
        name=user.name,
        is_active=True,
        parent_id=None,
        permissions=permission_group,
        has_admin_access=False,
    )


def make_user_data(
    role_ids: list[UUID],
    email: str = "new@example.com",
) -> UserCreate:
    return UserCreate(
        email=email, name="Новый", is_active=True, password=PASSWORD, role_ids=role_ids
    )


# ─────────────────────────────────────────────────────────────
# 1. Permission USERS.CREATE not found
# ─────────────────────────────────────────────────────────────


async def test_no_users_create_permission_raises(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
) -> None:
    """
    Actor without a USERS.CREATE group -> PermissionDeniedError, nothing created.
    """
    user = users_in_memory[1]
    actor = make_actor(user, [])
    data = make_user_data([role_in_memory.id])

    with pytest.raises(PermissionDeniedError):
        await create_user(
            actor,
            data,
            users=fake_users_repo,
            user_role=fake_user_roles_repo,
            role_permissions=fake_role_permissions_repo,
            user_direct_permissions=fake_user_direct_permissions_repo,
            user_permissions=fake_user_permissions_repo,
            roles=fake_roles_repo,
        )
    # Лишних пользователей нет
    created_ids = set(fake_users_repo.users.keys())
    assert created_ids == {u.id for u in users_in_memory} | {inactive_user_in_memory.id}


# ─────────────────────────────────────────────────────────────
# 2. Role the actor has no right to assign
# ─────────────────────────────────────────────────────────────


async def test_foreign_role_raises(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    role_in_memory: Role,
    system_role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
) -> None:
    """
    One of the roles is not allowed -> PermissionDeniedError, nothing created.

    Одна из ролей не разрешена -> PermissionDeniedError, ничего не создано.
    """
    user = users_in_memory[1]
    permission_group = await fake_user_permissions_repo.get_grouped_by_permission(user.id)
    actor = make_actor(user, permission_group)
    data = make_user_data([role_in_memory.id, system_role_in_memory.id])

    with pytest.raises(PermissionDeniedError):
        await create_user(
            actor,
            data,
            users=fake_users_repo,
            user_role=fake_user_roles_repo,
            role_permissions=fake_role_permissions_repo,
            user_direct_permissions=fake_user_direct_permissions_repo,
            user_permissions=fake_user_permissions_repo,
            roles=fake_roles_repo,
        )

    created_ids = set(fake_users_repo.users.keys())
    assert created_ids == {u.id for u in users_in_memory} | {inactive_user_in_memory.id}


# ─────────────────────────────────────────────────────────────
# 3. Email already taken
# ─────────────────────────────────────────────────────────────


async def test_email_taken_raises(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
) -> None:
    """
    Taken email (case-insensitive, ADR-USER-002) -> ConflictError, nothing created.
    """
    user = users_in_memory[0]
    permission_group = await fake_user_permissions_repo.get_grouped_by_permission(user.id)
    actor = make_actor(user, permission_group)
    data = make_user_data(
        [role_in_memory.id],
        email=user.email.upper(),  # ← другой регистр, но email занят
    )

    with pytest.raises(ConflictError):
        await create_user(
            actor,
            data,
            users=fake_users_repo,
            user_role=fake_user_roles_repo,
            role_permissions=fake_role_permissions_repo,
            user_direct_permissions=fake_user_direct_permissions_repo,
            user_permissions=fake_user_permissions_repo,
            roles=fake_roles_repo,
        )

    expected_ids = {u.id for u in users_in_memory} | {inactive_user_in_memory.id}
    assert set(fake_users_repo.users.keys()) == expected_ids


# ─────────────────────────────────────────────────────────────
# 4-7. Happy path
# ─────────────────────────────────────────────────────────────


async def test_returns_user_with_roles_output(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
) -> None:
    """
    Returns UserWithRolesOutput with all fields set; new user is inactive (BR-USERS-003).
    """
    user = users_in_memory[0]
    permission_group = await fake_user_permissions_repo.get_grouped_by_permission(user.id)
    actor = make_actor(user, permission_group)
    data = make_user_data([role_in_memory.id])

    result = await create_user(
        actor,
        data,
        users=fake_users_repo,
        user_role=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
        roles=fake_roles_repo,
    )

    assert isinstance(result, UserWithRolesOutput)
    assert isinstance(result.id, UUID)
    assert result.email == "new@example.com"
    assert result.name == "Новый"
    assert result.is_active is False  # BR-USERS-003
    assert result.parent_id == actor.id
    assert result.role_ids == [role_in_memory.id]


async def test_user_is_stored(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
) -> None:
    """
    The user is stored in the fake repository; the password is stored only as a hash.
    """
    user = users_in_memory[0]
    permission_group = await fake_user_permissions_repo.get_grouped_by_permission(user.id)
    actor = make_actor(user, permission_group)
    data = make_user_data([role_in_memory.id])

    result = await create_user(
        actor,
        data,
        users=fake_users_repo,
        user_role=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
        roles=fake_roles_repo,
    )

    # Юзер появился в хранилище фейка
    stored = fake_users_repo.users[result.id]
    assert stored is not None
    assert stored.email == "new@example.com"
    assert stored.name == "Новый"
    assert stored.parent_id == actor.id

    # Пароль хранится только в виде хеша
    assert stored.password_hash != PASSWORD
    assert is_verified_password(PASSWORD, stored.password_hash)


async def test_roles_are_linked(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    role_in_memory: Role,
    system_role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
) -> None:
    """
    One user-role link per requested role, nothing extra.
    """
    user = users_in_memory[0]
    permission_group = await fake_user_permissions_repo.get_grouped_by_permission(user.id)
    actor = make_actor(user, permission_group)
    data = make_user_data([role_in_memory.id, system_role_in_memory.id])

    result = await create_user(
        actor,
        data,
        users=fake_users_repo,
        user_role=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
        roles=fake_roles_repo,
    )

    # Связи для нового юзера — ровно по одной на каждую запрошенную роль
    new_user_links = {(uid, rid) for (uid, rid) in fake_user_roles_repo.links if uid == result.id}
    assert new_user_links == {
        (result.id, role_in_memory.id),
        (result.id, system_role_in_memory.id),
    }


async def test_permissions_are_synced(
    users_in_memory: list[User],
    role_in_memory: Role,
    system_role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
) -> None:
    """
    user_permissions holds exactly the conditions granted by the user's roles.
    """
    user = users_in_memory[0]
    permission_group = await fake_user_permissions_repo.get_grouped_by_permission(user.id)
    actor = make_actor(user, permission_group)
    data = make_user_data([role_in_memory.id, system_role_in_memory.id])

    result = await create_user(
        actor,
        data,
        users=fake_users_repo,
        user_role=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
        roles=fake_roles_repo,
    )

    # Conditions, которые дают роли нового юзера
    expected_conditions = set()
    for role_id in data.role_ids:
        for rid, cid in fake_role_permissions_repo.links:
            if rid == role_id:
                expected_conditions.add(cid)

    # Conditions, которые реально в user_permissions нового юзера
    actual_conditions = {cid for (uid, cid) in fake_user_permissions_repo.links if uid == result.id}

    assert actual_conditions == expected_conditions


# ─────────────────────────────────────────────────────────────
# Extra
# ─────────────────────────────────────────────────────────────


async def test_empty_role_ids_raises(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
) -> None:
    """
    Empty role_ids -> ValidationError, user is not created (BR-USERS-007).
    """
    user = users_in_memory[0]
    permission_group = await fake_user_permissions_repo.get_grouped_by_permission(user.id)
    actor = make_actor(user, permission_group)
    data = make_user_data([])  # ← пустой список

    with pytest.raises(ValidationError):
        await create_user(
            actor,
            data,
            users=fake_users_repo,
            user_role=fake_user_roles_repo,
            role_permissions=fake_role_permissions_repo,
            user_direct_permissions=fake_user_direct_permissions_repo,
            user_permissions=fake_user_permissions_repo,
            roles=fake_roles_repo,
        )

    expected_ids = {u.id for u in users_in_memory} | {inactive_user_in_memory.id}
    assert set(fake_users_repo.users.keys()) == expected_ids


async def test_inactive_role_raises(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    inactive_role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
) -> None:
    """
    Inactive role -> ValidationError, nothing created.
    """
    user = users_in_memory[0]
    permission_group = await fake_user_permissions_repo.get_grouped_by_permission(user.id)
    actor = make_actor(user, permission_group)
    data = make_user_data([inactive_role_in_memory.id])

    with pytest.raises(ValidationError):
        await create_user(
            actor,
            data,
            users=fake_users_repo,
            user_role=fake_user_roles_repo,
            role_permissions=fake_role_permissions_repo,
            user_direct_permissions=fake_user_direct_permissions_repo,
            user_permissions=fake_user_permissions_repo,
            roles=fake_roles_repo,
        )

    expected_ids = {u.id for u in users_in_memory} | {inactive_user_in_memory.id}
    assert set(fake_users_repo.users.keys()) == expected_ids
