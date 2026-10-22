from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.core.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.dto.system.user import CurrentUser
from app.dto.system.user_permission import GroupedPermission
from app.models.system import User
from app.models.system.permission_condition import PermissionCondition
from app.models.system.role import Role
from app.models.system.session import Session
from app.models.system.user_direct_permission import UserDirectPermission
from app.models.system.user_organization import UserOrganization
from app.models.system.user_permission import UserPermission
from app.models.system.user_role import UserRole
from app.use_cases.system.user.delete_user import delete_user
from tests.unit.fakes.organization import FakeOrganizationRepository
from tests.unit.fakes.role import FakeRoleRepository
from tests.unit.fakes.session_repository import FakeSessionRepository
from tests.unit.fakes.user_direct_permission import FakeUserDirectPermissionRepository
from tests.unit.fakes.user_permission import FakeUserPermissionRepository
from tests.unit.fakes.user_repository import FakeUserRepository
from tests.unit.fakes.user_role_repository import FakeUserRoleRepository


@pytest.fixture
def fakes(
    fake_users_repo: FakeUserRepository,
    fake_roles_repo: FakeRoleRepository,
    fake_organizations_repo: FakeOrganizationRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_sessions_repo: FakeSessionRepository,
    make_user_organizations_repo,
) -> dict:
    uor = make_user_organizations_repo()
    return {
        "users": fake_users_repo,
        "roles": fake_roles_repo,
        "organizations": fake_organizations_repo,
        "user_roles": fake_user_roles_repo,
        "user_permissions": fake_user_permissions_repo,
        "user_direct_permissions": fake_user_direct_permissions_repo,
        "sessions": fake_sessions_repo,
        "user_organizations": uor,
    }


def snapshot_fakes(fakes: dict) -> dict:
    """Capture repository state for side-effect assertions.

    Сохранить состояние репозиториев для проверки побочных эффектов.
    """
    users = fakes["users"]
    roles = fakes["roles"]
    organizations = fakes["organizations"]
    user_roles = fakes["user_roles"]
    user_organizations = fakes["user_organizations"]
    direct_permissions = fakes["user_direct_permissions"]
    permissions = fakes["user_permissions"]
    sessions = fakes["sessions"]

    return {
        "users": {
            user_id: (user.deleted_at, user.is_active) for user_id, user in users.users.items()
        },
        "roles": set(roles.roles),
        "organizations": set(organizations.organizations),
        "user_roles": set(user_roles.links),
        "user_organizations": set(user_organizations.links),
        "user_direct_permissions": set(direct_permissions.links),
        "user_permissions": set(permissions.links),
        "sessions": set(sessions.sessions),
    }


def add_target_dependencies(
    target: User,
    fakes: dict,
    condition: PermissionCondition,
    make_organization_in_memory,
) -> dict:
    """Create dependent entities owned by or linked to the target.

    Создать сущности, принадлежащие target или связанные с ним.
    """
    role = Role(
        id=uuid4(),
        name=f"Target role {uuid4()}",
        owner_id=target.id,
        description=None,
        is_system=False,
        is_active=True,
    )
    organization = make_organization_in_memory(owner=target)

    fakes["roles"].add(role)
    fakes["organizations"].add(organization)

    fakes["user_roles"].add(UserRole(user_id=target.id, role_id=role.id))

    fakes["user_organizations"].organizations[organization.id] = organization
    fakes["user_organizations"].add(
        UserOrganization(
            user_id=target.id,
            organization_id=organization.id,
        )
    )

    direct_link = UserDirectPermission(
        user_id=target.id,
        condition_id=condition.id,
    )
    fakes["user_direct_permissions"].links[(target.id, condition.id)] = direct_link

    effective_link = UserPermission(
        user_id=target.id,
        condition_id=condition.id,
    )
    fakes["user_permissions"].add(effective_link)

    session = Session(
        id=uuid4(),
        user_id=target.id,
        token_hash=uuid4().hex,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        last_used_at=datetime.now(UTC),
    )
    fakes["sessions"].add(session)

    return {
        "role": role,
        "organization": organization,
        "user_role": (target.id, role.id),
        "user_organization": (target.id, organization.id),
        "direct_permission": (target.id, condition.id),
        "effective_permission": (target.id, condition.id),
        "session": session,
    }


def make_actor(user: User, permissions: list[GroupedPermission]) -> CurrentUser:
    """Build CurrentUser from a user model and given permission groups.

    Собирает CurrentUser из модели пользователя и групп прав.
    """
    return CurrentUser(
        id=user.id,
        email=user.email,
        name=user.name,
        is_active=True,
        parent_id=None,
        children_count=0,
        permissions=permissions,
        has_admin_access=False,
    )


async def make_db_actor(user: User, repo: FakeUserPermissionRepository) -> CurrentUser:
    """Actor with the permissions the fake repo holds for this user.

    Актор с правами, которые fake-репозиторий хранит для этого пользователя.
    """
    return make_actor(user, await repo.get_grouped_by_permission(user.id))


# guard clauses


async def test_delete_user_not_found_raises(user_admin_in_memory: User, fakes: dict):
    """
    Target не существует → NotFoundError
    """
    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    with pytest.raises(NotFoundError):
        await delete_user(actor, uuid4(), **fakes)


async def test_delete_user_soft_deleted_target_raises(
    user_admin_in_memory: User, children_user_admin_in_memory: list[User], fakes: dict
):
    """
    Target soft-deleted → NotFoundError
    """
    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    children_user_admin_in_memory[0].deleted_at = datetime.now(UTC)
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(children_user_admin_in_memory[0])

    with pytest.raises(NotFoundError):
        await delete_user(actor, children_user_admin_in_memory[0].id, **fakes)


async def test_delete_user_self_deletion_raises(user_admin_in_memory: User, fakes: dict):
    """
    Actor удаляет себя → ValidationError
    """
    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    with pytest.raises(ValidationError):
        await delete_user(actor, user_admin_in_memory.id, **fakes)


async def test_delete_user_outside_subtree_raises(
    user_in_memory: User, user_admin_in_memory: User, fakes: dict
):
    """
    Target — сосед (вне поддерева) → PermissionDeniedError

    """
    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(user_in_memory)
    with pytest.raises(PermissionDeniedError):
        await delete_user(actor, user_in_memory.id, **fakes)


async def test_delete_user_ancestor_raises(
    user_admin_in_memory: User, children_user_admin_in_memory: list[User], fakes: dict
):
    """
    Target — предок actor → PermissionDeniedError
    """
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(children_user_admin_in_memory[0])

    actor = await make_db_actor(children_user_admin_in_memory[0], fakes["user_permissions"])
    with pytest.raises(PermissionDeniedError):
        await delete_user(actor, user_admin_in_memory.id, **fakes)


###### success


async def test_delete_user_direct_child_success(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    permission_conditions_allow_in_memory: list[PermissionCondition],
    make_organization_in_memory,
) -> None:
    """Delete a direct child and all dependent entities.

    Удалить прямого ребёнка и все зависимые сущности.
    """
    target = children_user_admin_in_memory[0]
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(target)

    condition = permission_conditions_allow_in_memory[0]

    dependencies = add_target_dependencies(
        target,
        fakes,
        condition,
        make_organization_in_memory,
    )

    actor = await make_db_actor(
        user_admin_in_memory,
        fakes["user_permissions"],
    )

    await delete_user(actor, target.id, **fakes)

    assert user_repo.users[target.id].deleted_at is not None
    assert user_repo.users[target.id].is_active is False

    assert dependencies["role"].id not in fakes["roles"].roles
    assert dependencies["organization"].id not in fakes["organizations"].organizations

    assert dependencies["user_role"] not in fakes["user_roles"].links
    assert dependencies["user_organization"] not in fakes["user_organizations"].links
    assert dependencies["direct_permission"] not in fakes["user_direct_permissions"].links
    assert dependencies["effective_permission"] not in fakes["user_permissions"].links
    assert dependencies["session"].id not in fakes["sessions"].sessions


async def test_delete_user_leaf_success(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    make_user_in_memory,
):
    """
    Target — лист (без потомков) → успех
    """
    target = children_user_admin_in_memory[0]

    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(target)
    deleted_count = sum(1 for u in user_repo.users.values() if u.deleted_at is not None)
    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    await delete_user(actor, target.id, **fakes)
    new_deleted_count = sum(1 for u in user_repo.users.values() if u.deleted_at is not None)

    assert deleted_count + 1 == new_deleted_count


async def test_delete_user_deletes_roles_of_subtree(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    make_user_in_memory,
) -> None:
    """Delete roles owned by the target and its child.

    Удалить роли, принадлежащие target и его ребёнку.
    """
    target = children_user_admin_in_memory[0]
    child = make_user_in_memory(
        email="delete-role-child@example.com",
        parent_id=target.id,
    )
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(target)
    user_repo.add(child)

    roles = [
        Role(
            id=uuid4(),
            name=f"Owned role {uuid4()}",
            owner_id=owner.id,
            is_system=False,
            is_active=True,
        )
        for owner in (target, child)
    ]
    for role in roles:
        fakes["roles"].add(role)

    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    await delete_user(actor, target.id, **fakes)

    assert all(role.id not in fakes["roles"].roles for role in roles)


async def test_delete_user_deletes_organizations_of_subtree(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    make_user_in_memory,
    make_organization_in_memory,
) -> None:
    """Delete organizations owned by subtree members.

    Удалить организации владельцев из поддерева.
    """
    target = children_user_admin_in_memory[0]
    child = make_user_in_memory(
        email="delete-org-child@example.com",
        parent_id=target.id,
    )
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(target)
    user_repo.add(child)

    organizations = [make_organization_in_memory(owner=owner) for owner in (target, child)]
    for organization in organizations:
        fakes["organizations"].add(organization)

    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    await delete_user(actor, target.id, **fakes)

    assert all(
        organization.id not in fakes["organizations"].organizations
        for organization in organizations
    )


async def test_delete_user_removes_user_role_links_of_subtree(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    make_user_in_memory,
) -> None:
    """Remove user-role links for every subtree member.

    Удалить связи пользователей с ролями для всех участников поддерева.
    """
    target = children_user_admin_in_memory[0]
    child = make_user_in_memory(
        email="delete-role-link-child@example.com",
        parent_id=target.id,
    )
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(target)
    user_repo.add(child)

    role = next(iter(fakes["roles"].roles.values()))
    links = [UserRole(user_id=owner.id, role_id=role.id) for owner in (target, child)]
    for link in links:
        fakes["user_roles"].add(link)

    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    await delete_user(actor, target.id, **fakes)

    assert all((link.user_id, link.role_id) not in fakes["user_roles"].links for link in links)


async def test_delete_user_removes_user_organization_links_of_subtree(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    make_user_in_memory,
    make_organization_in_memory,
) -> None:
    """Remove organization links for every subtree member.

    Удалить связи с организациями для всех участников поддерева.
    """
    target = children_user_admin_in_memory[0]
    child = make_user_in_memory(
        email="delete-org-link-child@example.com",
        parent_id=target.id,
    )
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(target)
    user_repo.add(child)

    organization = make_organization_in_memory(owner=user_admin_in_memory)
    fakes["user_organizations"].organizations[organization.id] = organization

    links = [
        UserOrganization(
            user_id=owner.id,
            organization_id=organization.id,
        )
        for owner in (target, child)
    ]
    for link in links:
        fakes["user_organizations"].add(link)

    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    await delete_user(actor, target.id, **fakes)

    assert all(
        (link.user_id, link.organization_id) not in fakes["user_organizations"].links
        for link in links
    )


async def test_delete_user_removes_sessions_of_subtree(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    make_user_in_memory,
) -> None:
    """Remove sessions belonging to the subtree.

    Удалить сессии пользователей из поддерева.
    """
    target = children_user_admin_in_memory[0]
    child = make_user_in_memory(
        email="delete-session-child@example.com",
        parent_id=target.id,
    )
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(target)
    user_repo.add(child)

    sessions = [
        Session(
            id=uuid4(),
            user_id=owner.id,
            token_hash=uuid4().hex,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            last_used_at=datetime.now(UTC),
        )
        for owner in (target, child)
    ]
    for session in sessions:
        fakes["sessions"].add(session)

    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    await delete_user(actor, target.id, **fakes)

    assert all(session.id not in fakes["sessions"].sessions for session in sessions)


async def test_delete_user_removes_direct_permissions_of_subtree(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    make_user_in_memory,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> None:
    """Remove direct permissions for every subtree member.

    Удалить прямые права всех участников поддерева.
    """
    target = children_user_admin_in_memory[0]
    child = make_user_in_memory(
        email="delete-direct-permission-child@example.com",
        parent_id=target.id,
    )
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(target)
    user_repo.add(child)
    condition = permission_conditions_allow_in_memory[0]
    links = [
        UserDirectPermission(user_id=owner.id, condition_id=condition.id)
        for owner in (target, child)
    ]
    for link in links:
        fakes["user_direct_permissions"].links[(link.user_id, link.condition_id)] = link

    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    await delete_user(actor, target.id, **fakes)

    assert all(
        (link.user_id, link.condition_id) not in fakes["user_direct_permissions"].links
        for link in links
    )


async def test_delete_user_removes_effective_permissions_of_subtree(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    make_user_in_memory,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> None:
    """Remove effective permissions for every subtree member.

    Удалить вычисленные права всех участников поддерева.
    """
    target = children_user_admin_in_memory[0]
    child = make_user_in_memory(
        email="delete-effective-permission-child@example.com",
        parent_id=target.id,
    )
    user_repo: FakeUserRepository = fakes["users"]
    user_repo.add(target)
    user_repo.add(child)

    condition = permission_conditions_allow_in_memory[0]
    links = [
        UserPermission(user_id=owner.id, condition_id=condition.id) for owner in (target, child)
    ]
    for link in links:
        fakes["user_permissions"].add(link)

    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    await delete_user(actor, target.id, **fakes)

    assert all(
        (link.user_id, link.condition_id) not in fakes["user_permissions"].links for link in links
    )


async def test_delete_user_not_found_has_no_side_effects(
    user_admin_in_memory: User,
    fakes: dict,
) -> None:
    """Leave all repositories unchanged when target is missing.

    Не менять состояние репозиториев, если target не найден.
    """
    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    before = snapshot_fakes(fakes)

    with pytest.raises(NotFoundError):
        await delete_user(actor, uuid4(), **fakes)

    assert snapshot_fakes(fakes) == before


async def test_delete_user_outside_subtree_has_no_side_effects(
    user_admin_in_memory: User,
    user_in_memory: User,
    fakes: dict,
) -> None:
    """Leave all repositories unchanged when target is outside the subtree.

    Не менять состояние репозиториев, если target вне поддерева.
    """
    fakes["users"].add(user_in_memory)
    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    before = snapshot_fakes(fakes)

    with pytest.raises(PermissionDeniedError):
        await delete_user(actor, user_in_memory.id, **fakes)

    assert snapshot_fakes(fakes) == before


async def test_delete_user_self_deletion_has_no_side_effects(
    user_admin_in_memory: User,
    fakes: dict,
) -> None:
    """Leave all repositories unchanged when actor targets themselves.

    Не менять состояние репозиториев при попытке удалить себя.
    """
    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    before = snapshot_fakes(fakes)

    with pytest.raises(ValidationError):
        await delete_user(actor, user_admin_in_memory.id, **fakes)

    assert snapshot_fakes(fakes) == before


async def test_delete_user_multiple_children(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    fakes: dict,
    make_user_in_memory,
) -> None:
    """Soft-delete a target with multiple descendants.

    Мягко удалить target вместе с несколькими потомками.
    """
    target = children_user_admin_in_memory[0]
    children = [
        make_user_in_memory(
            email=f"multiple-child-{index}@example.com",
            parent_id=target.id,
        )
        for index in range(3)
    ]

    for user in [target, *children]:
        fakes["users"].add(user)

    actor = await make_db_actor(user_admin_in_memory, fakes["user_permissions"])
    await delete_user(actor, target.id, **fakes)

    for user in [target, *children]:
        assert user.deleted_at is not None
        assert user.is_active is False
