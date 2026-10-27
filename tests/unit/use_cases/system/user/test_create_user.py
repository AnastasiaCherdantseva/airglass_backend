"""Unit tests for the create_user use case (fake repositories, no DB).

Юнит-тесты юзкейса create_user (фейковые репозитории, без БД).
"""

from collections.abc import Callable
from typing import Any
from uuid import UUID, uuid4

import pytest

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.core.security import is_verified_password
from app.dto import CurrentUser, GroupedPermission, UserCreate, UserWithRolesOutput
from app.dto.system.organization import OrganizationData
from app.dto.system.permission_condition import PermissionConditionAllOutPut
from app.models.system import ConditionType, PermissionEffect, Role, User
from app.use_cases.system.user.create_user import create_user
from tests.unit.fakes.organization import FakeOrganizationRepository
from tests.unit.fakes.role import FakeRoleRepository
from tests.unit.fakes.role_permission import FakeRolePermissionRepository
from tests.unit.fakes.user_direct_permission import FakeUserDirectPermissionRepository
from tests.unit.fakes.user_organization_repository import FakeUserOrganizationRepository
from tests.unit.fakes.user_permission import FakeUserPermissionRepository
from tests.unit.fakes.user_repository import FakeUserRepository
from tests.unit.fakes.user_role_repository import FakeUserRoleRepository

PASSWORD = "secretsecretsecret"
CREATE_CODE = "USERS.CREATE"


# ─────────────────────────────────────────────────────────────
# Helpers / Хелперы
# ─────────────────────────────────────────────────────────────


def make_condition(
    *,
    type_: ConditionType = ConditionType.ROLE,
    # effect: PermissionEffect = PermissionEffect.ALLOW,
    is_active: bool = True,
    role_id: UUID | None = None,
) -> PermissionConditionAllOutPut:
    """Build a condition DTO.

    Собирает DTO условия права.
    """
    return PermissionConditionAllOutPut(
        id=uuid4(),
        permission_id=uuid4(),
        category_id=None,
        role_id=role_id,
        media_type_id=None,
        # effect=effect,
        type=type_,
        is_active=is_active,
    )


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


def make_user_data(
    role_ids: list[UUID],
    email: str = "new@example.com",
    organization_ids: list[UUID] | None = None,
) -> UserCreate:
    """Build UserCreate input data.

    Собирает входные данные UserCreate.
    """
    return UserCreate(
        email=email,
        name="Новый",
        is_active=True,
        password=PASSWORD,
        role_ids=role_ids,
        organization_ids=organization_ids or [],
    )


async def make_db_actor(user: User, repo: FakeUserPermissionRepository) -> CurrentUser:
    """Actor with the permissions the fake repo holds for this user.

    Актор с правами, которые fake-репозиторий хранит для этого пользователя.
    """
    return make_actor(user, await repo.get_grouped_by_permission(user.id))


@pytest.fixture
def deps(
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
    fake_organizations_repo: FakeOrganizationRepository,
    make_user_organizations_repo: Callable[..., FakeUserOrganizationRepository],
) -> dict[str, Any]:
    """Keyword arguments for create_user (thin wrapper over existing fakes).

    Именованные аргументы для create_user (обёртка над готовыми fake'ами).
    """
    return {
        "users": fake_users_repo,
        "user_role": fake_user_roles_repo,
        "role_permissions": fake_role_permissions_repo,
        "user_direct_permissions": fake_user_direct_permissions_repo,
        "user_permissions": fake_user_permissions_repo,
        "roles": fake_roles_repo,
        "organizations": fake_organizations_repo,
        "user_organizations": make_user_organizations_repo(
            *fake_organizations_repo.organizations.values()
        ),
    }


def snapshot(deps: dict[str, Any]) -> tuple[set[UUID], set[tuple[UUID, UUID]], set[Any], set[Any]]:
    """Capture state that create_user is allowed to change.

    Снимок состояния, которое может менять create_user.
    """
    return (
        set(deps["users"].users),
        set(deps["user_role"].links),
        set(deps["user_permissions"].links),
        set(deps["user_organizations"].links),
    )


# ─────────────────────────────────────────────────────────────
# 1-2. USERS.CREATE permission
# ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "groups",
    [
        pytest.param([], id="no_permissions"),
        pytest.param(
            [GroupedPermission(id=uuid4(), code="USERS.READ", conditions=[make_condition()])],
            id="other_permission_only",
        ),
    ],
)
async def test_no_users_create_permission_raises(
    users_in_memory: list[User],
    role_in_memory: Role,
    deps: dict[str, Any],
    groups: list[GroupedPermission],
) -> None:
    """No USERS.CREATE group -> PermissionDeniedError, nothing created.

    Нет группы USERS.CREATE -> PermissionDeniedError, ничего не создано.
    """
    actor = make_actor(users_in_memory[1], groups)
    before = snapshot(deps)

    with pytest.raises(PermissionDeniedError):
        await create_user(actor, make_user_data([role_in_memory.id]), **deps)

    assert snapshot(deps) == before


@pytest.mark.parametrize(
    ("type_", "is_active"),
    [
        pytest.param(ConditionType.SUBTREE, True, id="wrong_type"),
        pytest.param(ConditionType.ROLE, False, id="inactive"),
        pytest.param(None, None, id="no_conditions"),
    ],
)
async def test_no_suitable_role_condition_raises(
    users_in_memory: list[User],
    role_in_memory: Role,
    deps: dict[str, Any],
    type_: ConditionType | None,
    effect: PermissionEffect | None,
    is_active: bool | None,
) -> None:
    """USERS.CREATE without an active ROLE+ALLOW condition -> PermissionDeniedError.

    USERS.CREATE без активного условия ROLE+ALLOW -> PermissionDeniedError.
    """
    conditions = (
        []
        if type_ is None
        else [make_condition(type_=type_, is_active=is_active, role_id=role_in_memory.id)]
    )
    group = GroupedPermission(id=uuid4(), code=CREATE_CODE, conditions=conditions)
    actor = make_actor(users_in_memory[1], [group])
    before = snapshot(deps)

    with pytest.raises(PermissionDeniedError):
        await create_user(actor, make_user_data([role_in_memory.id]), **deps)

    assert snapshot(deps) == before


# ─────────────────────────────────────────────────────────────
# 3-6. Roles
# ─────────────────────────────────────────────────────────────


async def test_empty_role_ids_raises(
    users_in_memory: list[User],
    deps: dict[str, Any],
    fake_user_permissions_repo: FakeUserPermissionRepository,
) -> None:
    """Empty role_ids -> ValidationError, nothing created.

    Пустой role_ids -> ValidationError, ничего не создано.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    before = snapshot(deps)

    with pytest.raises(ValidationError):
        await create_user(actor, make_user_data([]), **deps)

    assert snapshot(deps) == before


async def test_role_not_found_raises(
    users_in_memory: list[User],
    role_in_memory: Role,
    deps: dict[str, Any],
    fake_user_permissions_repo: FakeUserPermissionRepository,
) -> None:
    """One of the roles does not exist -> NotFoundError, nothing created.

    Одна из ролей не существует -> NotFoundError, ничего не создано.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    before = snapshot(deps)

    with pytest.raises(NotFoundError):
        await create_user(actor, make_user_data([role_in_memory.id, uuid4()]), **deps)

    assert snapshot(deps) == before


async def test_inactive_role_raises(
    users_in_memory: list[User],
    role_in_memory: Role,
    inactive_role_in_memory: Role,
    deps: dict[str, Any],
    fake_user_permissions_repo: FakeUserPermissionRepository,
) -> None:
    """One of the roles is inactive -> ValidationError, nothing created.

    Одна из ролей неактивна -> ValidationError, ничего не создано.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    before = snapshot(deps)

    with pytest.raises(ValidationError):
        await create_user(
            actor, make_user_data([role_in_memory.id, inactive_role_in_memory.id]), **deps
        )

    assert snapshot(deps) == before


async def test_role_not_allowed_raises(
    users_in_memory: list[User],
    role_in_memory: Role,
    system_role_in_memory: Role,
    deps: dict[str, Any],
    fake_user_permissions_repo: FakeUserPermissionRepository,
) -> None:
    """Role outside the actor's allowed set -> PermissionDeniedError.

    Роль вне разрешённых актору -> PermissionDeniedError.
    """
    # users_in_memory[1] is allowed to assign role_in_memory only
    actor = await make_db_actor(users_in_memory[1], fake_user_permissions_repo)
    before = snapshot(deps)

    with pytest.raises(PermissionDeniedError):
        await create_user(
            actor, make_user_data([role_in_memory.id, system_role_in_memory.id]), **deps
        )

    assert snapshot(deps) == before


# ─────────────────────────────────────────────────────────────
# 7. Email
# ─────────────────────────────────────────────────────────────


async def test_email_taken_case_insensitive_raises(
    users_in_memory: list[User],
    role_in_memory: Role,
    deps: dict[str, Any],
    fake_user_permissions_repo: FakeUserPermissionRepository,
) -> None:
    """Taken email in another case -> ConflictError, nothing created.

    Занятый email в другом регистре -> ConflictError, ничего не создано.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    data = make_user_data([role_in_memory.id], email=users_in_memory[2].email.upper())
    before = snapshot(deps)

    with pytest.raises(ConflictError):
        await create_user(actor, data, **deps)

    assert snapshot(deps) == before


# ─────────────────────────────────────────────────────────────
# 11-12. Success
# ─────────────────────────────────────────────────────────────


async def test_success_single_role(
    users_in_memory: list[User],
    role_in_memory: Role,
    deps: dict[str, Any],
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Single role: full output, stored user, one link, synced permissions.

    Одна роль: полный ответ, сохранённый юзер, одна связь, права синхронизированы.
    """
    actor = await make_db_actor(users_in_memory[1], fake_user_permissions_repo)
    data = make_user_data([role_in_memory.id])
    known_ids = set(fake_users_repo.users)

    result = await create_user(actor, data, **deps)

    # Response
    assert isinstance(result, UserWithRolesOutput)
    assert result.id not in known_ids
    assert result.email == data.email
    assert result.name == data.name
    assert result.is_active is False  # BR-USERS-003
    stored = fake_users_repo.users[result.id]
    assert stored.is_active is False
    assert result.parent_id == actor.id
    assert stored.parent_id == actor.id
    assert result.role_ids == data.role_ids
    assert result.children_count == await fake_users_repo.count_by_parent_id(result.id)

    # Stored user, password only as a hash
    stored = fake_users_repo.users[result.id]
    assert stored.password_hash != PASSWORD
    assert is_verified_password(PASSWORD, stored.password_hash)

    # Exactly one UserRole link
    links = {k for k in fake_user_roles_repo.links if k[0] == result.id}
    assert links == {(result.id, role_in_memory.id)}

    # sync_user_permissions ran: conditions of the role
    expected = {cid for rid, cid in fake_role_permissions_repo.links if rid == role_in_memory.id}
    actual = {cid for uid, cid in fake_user_permissions_repo.links if uid == result.id}
    assert expected
    assert actual == expected


async def test_success_multiple_roles(
    users_in_memory: list[User],
    role_in_memory: Role,
    system_role_in_memory: Role,
    deps: dict[str, Any],
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """Several roles: link per role, union of their conditions.

    Несколько ролей: связь на каждую роль, объединение их conditions.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    role_ids = [role_in_memory.id, system_role_in_memory.id]

    result = await create_user(actor, make_user_data(role_ids), **deps)

    links = {k for k in fake_user_roles_repo.links if k[0] == result.id}
    assert links == {(result.id, rid) for rid in role_ids}

    expected = {cid for rid, cid in fake_role_permissions_repo.links if rid in role_ids}
    actual = {cid for uid, cid in fake_user_permissions_repo.links if uid == result.id}
    assert expected
    assert actual == expected


# ─────────────────────────────────────────────────────────────
# 13-14. Organizations
# ─────────────────────────────────────────────────────────────


async def test_success_with_organizations(
    users_in_memory: list[User],
    role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
    fake_organizations_repo: FakeOrganizationRepository,
    make_user_organizations_repo: Callable[..., FakeUserOrganizationRepository],
) -> None:
    """Success with one owned organization: a user-organization link is created.

    Успех с одной своей организацией: создаётся связь пользователь–организация.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    org = await fake_organizations_repo.create_for_user(
        actor.id,
        OrganizationData(name="ООО Своя", inn="123456789012", address="г. Москва"),
    )
    user_organizations = make_user_organizations_repo(org)

    result = await create_user(
        actor,
        make_user_data([role_in_memory.id], organization_ids=[org.id]),
        users=fake_users_repo,
        user_role=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
        roles=fake_roles_repo,
        organizations=fake_organizations_repo,
        user_organizations=user_organizations,
    )

    links = {k for k in user_organizations.links if k[0] == result.id}
    assert links == {(result.id, org.id)}


async def test_success_with_several_organizations(
    users_in_memory: list[User],
    role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
    fake_organizations_repo: FakeOrganizationRepository,
    make_user_organizations_repo: Callable[..., FakeUserOrganizationRepository],
) -> None:
    """Success with several owned organizations: a link per organization.

    Успех с несколькими своими организациями: связь на каждую организацию.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    org_a = await fake_organizations_repo.create_for_user(
        actor.id,
        OrganizationData(name="ООО Своя", inn="123456789012", address="г. Москва"),
    )
    org_b = await fake_organizations_repo.create_for_user(
        actor.id,
        OrganizationData(name="ООО Своя2", inn="123456789013", address="г. Москва"),
    )
    user_organizations = make_user_organizations_repo(org_a, org_b)

    result = await create_user(
        actor,
        make_user_data([role_in_memory.id], organization_ids=[org_a.id, org_b.id]),
        users=fake_users_repo,
        user_role=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
        roles=fake_roles_repo,
        organizations=fake_organizations_repo,
        user_organizations=user_organizations,
    )

    links = {k for k in user_organizations.links if k[0] == result.id}
    assert links == {(result.id, org_a.id), (result.id, org_b.id)}


async def test_success_without_organizations_creates_no_links(
    users_in_memory: list[User],
    role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
    fake_organizations_repo: FakeOrganizationRepository,
    make_user_organizations_repo: Callable[..., FakeUserOrganizationRepository],
) -> None:
    """No organization_ids: no user-organization links are created.

    Без organization_ids: связи пользователь–организация не создаются.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    user_organizations = make_user_organizations_repo()

    result = await create_user(
        actor,
        make_user_data([role_in_memory.id], organization_ids=[]),
        users=fake_users_repo,
        user_role=fake_user_roles_repo,
        role_permissions=fake_role_permissions_repo,
        user_direct_permissions=fake_user_direct_permissions_repo,
        user_permissions=fake_user_permissions_repo,
        roles=fake_roles_repo,
        organizations=fake_organizations_repo,
        user_organizations=user_organizations,
    )

    assert {k for k in user_organizations.links if k[0] == result.id} == set()


async def test_organization_not_found_raises(
    users_in_memory: list[User],
    role_in_memory: Role,
    deps: dict[str, Any],
    fake_user_permissions_repo: FakeUserPermissionRepository,
) -> None:
    """Unknown organization id -> NotFoundError, nothing created.

    Неизвестный id организации -> NotFoundError, ничего не создано.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    before = snapshot(deps)

    with pytest.raises(NotFoundError):
        await create_user(
            actor,
            make_user_data([role_in_memory.id], organization_ids=[uuid4()]),
            **deps,
        )

    assert snapshot(deps) == before


async def test_foreign_organization_raises(
    users_in_memory: list[User],
    role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
    fake_organizations_repo: FakeOrganizationRepository,
    make_user_organizations_repo: Callable[..., FakeUserOrganizationRepository],
) -> None:
    """Organization owned by another user -> PermissionDeniedError, nothing created.

    Организация, принадлежащая другому пользователю -> PermissionDeniedError,
    ничего не создано.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    foreign_org = await fake_organizations_repo.create_for_user(
        users_in_memory[1],
        OrganizationData(name="ООО Чужая", inn="123456789543", address="г. Москва"),
    )
    user_organizations = make_user_organizations_repo(foreign_org)

    users_before = set(fake_users_repo.users)
    role_links_before = set(fake_user_roles_repo.links)

    with pytest.raises(PermissionDeniedError):
        await create_user(
            actor,
            make_user_data([role_in_memory.id], organization_ids=[foreign_org.id]),
            users=fake_users_repo,
            user_role=fake_user_roles_repo,
            role_permissions=fake_role_permissions_repo,
            user_direct_permissions=fake_user_direct_permissions_repo,
            user_permissions=fake_user_permissions_repo,
            roles=fake_roles_repo,
            organizations=fake_organizations_repo,
            user_organizations=user_organizations,
        )

    assert set(fake_users_repo.users) == users_before
    assert set(fake_user_roles_repo.links) == role_links_before


async def test_mixed_own_and_foreign_organizations_raises(
    users_in_memory: list[User],
    role_in_memory: Role,
    fake_users_repo: FakeUserRepository,
    fake_user_roles_repo: FakeUserRoleRepository,
    fake_role_permissions_repo: FakeRolePermissionRepository,
    fake_user_direct_permissions_repo: FakeUserDirectPermissionRepository,
    fake_user_permissions_repo: FakeUserPermissionRepository,
    fake_roles_repo: FakeRoleRepository,
    fake_organizations_repo: FakeOrganizationRepository,
    make_user_organizations_repo: Callable[..., FakeUserOrganizationRepository],
) -> None:
    """One own + one foreign organization -> PermissionDeniedError, no side effects.

    Одна своя + одна чужая организация -> PermissionDeniedError,
    без побочных эффектов.
    """
    actor = await make_db_actor(users_in_memory[0], fake_user_permissions_repo)
    own_org = await fake_organizations_repo.create_for_user(
        actor.id,
        OrganizationData(name="ООО svoya", inn="123451239543", address="г. Москва"),
    )
    foreign_org = await fake_organizations_repo.create_for_user(
        users_in_memory[1],
        OrganizationData(name="ООО Чужая", inn="123456789543", address="г. Москва"),
    )
    user_organizations = make_user_organizations_repo(own_org, foreign_org)

    users_before = set(fake_users_repo.users)
    role_links_before = set(fake_user_roles_repo.links)

    with pytest.raises(PermissionDeniedError):
        await create_user(
            actor,
            make_user_data(
                [role_in_memory.id],
                organization_ids=[own_org.id, foreign_org.id],
            ),
            users=fake_users_repo,
            user_role=fake_user_roles_repo,
            role_permissions=fake_role_permissions_repo,
            user_direct_permissions=fake_user_direct_permissions_repo,
            user_permissions=fake_user_permissions_repo,
            roles=fake_roles_repo,
            organizations=fake_organizations_repo,
            user_organizations=user_organizations,
        )

    assert set(fake_users_repo.users) == users_before
    assert set(fake_user_roles_repo.links) == role_links_before
