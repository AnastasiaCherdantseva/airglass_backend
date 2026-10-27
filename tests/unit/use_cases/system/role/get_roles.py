"""Unit tests for the get_roles use case.

Юнит-тесты сценария get_roles.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.core.exceptions import ConflictError, PermissionDeniedError
from app.dto.system.permission_condition import PermissionConditionAllOutPut
from app.dto.system.user import CurrentUser
from app.dto.system.user_permission import GroupedPermission
from app.models import Role
from app.models.system import ConditionType
from app.use_cases.system.role.get_roles import get_roles
from tests.unit.fakes.role import FakeRoleRepository
from tests.unit.fakes.role_permission import FakeRolePermissionRepository

ROLES_READ = "ROLES.READ"


def make_condition_dto(
    *,
    role_id: UUID | None,
    is_active: bool = True,
) -> PermissionConditionAllOutPut:
    """Create a permission condition DTO for the current user.

    Создать DTO условия права для текущего пользователя.
    """
    return PermissionConditionAllOutPut(
        id=uuid4(),
        permission_id=uuid4(),
        category_id=None,
        role_id=role_id,
        media_type_id=None,
        type=ConditionType.ROLE,
        is_active=is_active,
    )


def make_actor(
    *,
    actor_id: UUID | None = None,
    conditions: list[PermissionConditionAllOutPut] | None = None,
    include_roles_read: bool = True,
) -> CurrentUser:
    """Create a current user with configurable permissions.

    Создать текущего пользователя с настраиваемыми правами.
    """
    permissions = (
        [
            GroupedPermission(
                id=uuid4(),
                code=ROLES_READ,
                conditions=conditions or [],
            )
        ]
        if include_roles_read
        else []
    )

    return CurrentUser(
        id=actor_id or uuid4(),
        email="actor@example.com",
        name="Actor",
        is_active=True,
        parent_id=None,
        children_count=0,
        email_verified=True,
        permissions=permissions,
        has_admin_access=False,
    )


def make_role(
    *,
    role_id: UUID | None = None,
    owner_id: UUID | None = None,
    name: str = "Test role",
    is_active: bool = True,
) -> Role:
    """Create a role model for testing.

    Создать модель роли для тестирования.
    """
    now = datetime.now(UTC)

    return Role(
        id=role_id or uuid4(),
        name=name,
        owner_id=owner_id,
        description=None,
        is_system=owner_id is None,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_get_roles_requires_roles_read_permission() -> None:
    """Reject an actor without ROLES.READ.

    Отклонить запрос пользователя без ROLES.READ.
    """
    actor = make_actor(include_roles_read=False)

    with pytest.raises(PermissionDeniedError):
        await get_roles(
            actor,
            roles=FakeRoleRepository(),
            role_permissions=FakeRolePermissionRepository(),
        )


@pytest.mark.asyncio
async def test_get_roles_rejects_active_condition_without_role_id() -> None:
    """Reject an active condition without a role ID.

    Отклонить активное условие без идентификатора роли.
    """
    actor = make_actor(
        conditions=[make_condition_dto(role_id=None)],
    )

    with pytest.raises(ConflictError):
        await get_roles(
            actor,
            roles=FakeRoleRepository(),
            role_permissions=FakeRolePermissionRepository(),
        )


@pytest.mark.asyncio
async def test_get_roles_ignores_inactive_condition_without_role_id() -> None:
    """Ignore an inactive condition without a role ID.

    Игнорировать неактивное условие без идентификатора роли.
    """
    actor = make_actor(
        conditions=[
            make_condition_dto(role_id=None, is_active=False),
        ],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository(),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_roles_ignores_inactive_conditions() -> None:
    """Ignore roles referenced only by inactive conditions.

    Игнорировать роли, указанные только в неактивных условиях.
    """
    role = make_role()
    actor = make_actor(
        conditions=[
            make_condition_dto(role_id=role.id, is_active=False),
        ],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository([role]),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_roles_returns_roles_from_active_conditions() -> None:
    """Return roles referenced by active conditions only.

    Вернуть только роли, указанные в активных условиях.
    """
    first_role = make_role()
    second_role = make_role()
    inactive_role = make_role()

    actor = make_actor(
        conditions=[
            make_condition_dto(role_id=first_role.id),
            make_condition_dto(role_id=second_role.id),
            make_condition_dto(
                role_id=inactive_role.id,
                is_active=False,
            ),
        ],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository(
            [first_role, second_role, inactive_role],
        ),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert {role.id for role in result} == {
        first_role.id,
        second_role.id,
    }


@pytest.mark.asyncio
async def test_get_roles_deduplicates_role_ids() -> None:
    """Return a role only once when several conditions reference it.

    Вернуть роль один раз, если на неё ссылаются несколько условий.
    """
    role = make_role()
    actor = make_actor(
        conditions=[
            make_condition_dto(role_id=role.id),
            make_condition_dto(role_id=role.id),
        ],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository([role]),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert [item.id for item in result] == [role.id]


@pytest.mark.asyncio
async def test_get_roles_returns_empty_when_no_active_conditions() -> None:
    """Return an empty list when no active conditions exist.

    Вернуть пустой список, если активных условий нет.
    """
    actor = make_actor(
        conditions=[
            make_condition_dto(role_id=uuid4(), is_active=False),
        ],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository(),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_roles_returns_empty_when_roles_are_not_found() -> None:
    """Return an empty list when referenced roles do not exist.

    Вернуть пустой список, если указанные роли не найдены.
    """
    actor = make_actor(
        conditions=[make_condition_dto(role_id=uuid4())],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository(),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_roles_returns_empty_permissions_without_links() -> None:
    """Return roles with empty permissions when no links exist.

    Вернуть роли с пустым списком permissions, если связей нет.
    """
    role = make_role()
    actor = make_actor(
        conditions=[make_condition_dto(role_id=role.id)],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository([role]),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert len(result) == 1
    assert result[0].id == role.id
    assert result[0].permissions == []


@pytest.mark.asyncio
async def test_get_roles_includes_inactive_roles() -> None:
    """Include inactive roles referenced by active conditions.

    Включить неактивные роли, указанные в активных условиях.
    """
    role = make_role(is_active=False)
    actor = make_actor(
        conditions=[make_condition_dto(role_id=role.id)],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository([role]),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert len(result) == 1
    assert result[0].id == role.id
    assert result[0].is_active is False


@pytest.mark.asyncio
async def test_get_roles_sorts_non_owned_roles_before_owned_roles() -> None:
    """Place roles owned by others before roles owned by the actor.

    Разместить чужие и системные роли перед собственными ролями актора.
    """
    actor_id = uuid4()

    system_role = make_role(
        role_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=None,
    )
    other_role = make_role(
        role_id=UUID("00000000-0000-0000-0000-000000000002"),
        owner_id=uuid4(),
    )
    own_role = make_role(
        role_id=UUID("00000000-0000-0000-0000-000000000003"),
        owner_id=actor_id,
    )

    actor = make_actor(
        actor_id=actor_id,
        conditions=[
            make_condition_dto(role_id=own_role.id),
            make_condition_dto(role_id=other_role.id),
            make_condition_dto(role_id=system_role.id),
        ],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository([own_role, system_role, other_role]),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert [role.id for role in result] == [
        system_role.id,
        other_role.id,
        own_role.id,
    ]


@pytest.mark.asyncio
async def test_get_roles_sorts_roles_by_id_within_owner_group() -> None:
    """Sort roles by ID within each ownership group.

    Сортировать роли по ID внутри каждой группы владельцев.
    """
    actor_id = uuid4()

    first_id = UUID("00000000-0000-0000-0000-000000000001")
    second_id = UUID("00000000-0000-0000-0000-000000000002")
    own_first_id = UUID("00000000-0000-0000-0000-000000000003")
    own_second_id = UUID("00000000-0000-0000-0000-000000000004")

    roles = [
        make_role(role_id=own_second_id, owner_id=actor_id),
        make_role(role_id=second_id),
        make_role(role_id=own_first_id, owner_id=actor_id),
        make_role(role_id=first_id),
    ]

    actor = make_actor(
        actor_id=actor_id,
        conditions=[make_condition_dto(role_id=role.id) for role in roles],
    )

    result = await get_roles(
        actor,
        roles=FakeRoleRepository(roles),
        role_permissions=FakeRolePermissionRepository(),
    )

    assert [role.id for role in result] == [
        first_id,
        second_id,
        own_first_id,
        own_second_id,
    ]


@pytest.mark.asyncio
async def test_get_roles_rejects_actor_with_only_unrelated_permission() -> None:
    """Reject an actor who has no ROLES.READ permission.

    Отклонить запрос пользователя, у которого нет права ROLES.READ.
    """
    actor = make_actor(include_roles_read=False)
    with pytest.raises(PermissionDeniedError):
        await get_roles(
            actor,
            roles=FakeRoleRepository(),
            role_permissions=FakeRolePermissionRepository(),
        )
