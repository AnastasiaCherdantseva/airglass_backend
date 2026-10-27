"""Tests for PermissionConditionRepository."""

from uuid import uuid4

import pytest_asyncio

from app.models.system import ConditionType
from app.models.system.permission import PermissionAction, PermissionResource
from app.models.system.role import Role
from app.repositories.system.permission_condition import PermissionConditionRepository

# ─────────────────────────────────────────────────────────────────────
# get_by_permission
# ─────────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def roles(role: Role, system_role: Role, inactive_role: Role):
    return [role, system_role, inactive_role]


async def make_conditions_with_roles(permission, make_condition, roles: list[Role]):
    conditions = []
    for r in roles:
        conditions.append(await make_condition(permission, type_=ConditionType.ROLE, role_id=r.id))
    return conditions


async def test_get_by_permission_returns_all_conditions(
    db_session, make_permission, make_condition, roles
):
    """Возвращает все conditions для permission'а"""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    await make_conditions_with_roles(permission, make_condition, roles)
    result = await repo.get_by_permission(permission.id)

    assert len(result) == 3
    assert all(c.permission_id == permission.id for c in result)


async def test_get_by_permission_empty_for_unknown(
    db_session, permissions, permission_conditions_allow
):
    """Возвращает пустой список для permission'а без conditions."""
    repo = PermissionConditionRepository(db_session)
    unknown_id = uuid4()

    result = await repo.get_by_permission(unknown_id)

    assert result == []


async def test_get_by_permission_filter_is_active_true(
    db_session, make_permission, make_condition, roles
):
    """Фильтр is_active=True возвращает только активные."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    res = await make_conditions_with_roles(permission, make_condition, roles)

    res[0].is_active = False
    await db_session.flush()
    result = await repo.get_by_permission(permission.id, is_active=True)

    assert len(result) == 2
    assert result[0].is_active is True


async def test_get_by_permission_filter_is_active_false(
    db_session, make_permission, make_condition, roles
):
    """Фильтр is_active=False возвращает только неактивные."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    res = await make_conditions_with_roles(permission, make_condition, roles)

    res[0].is_active = False
    await db_session.flush()
    result = await repo.get_by_permission(permission.id, is_active=False)

    assert len(result) == 1
    assert result[0].is_active is False


# ─────────────────────────────────────────────────────────────────────
# get_by_ids
# ─────────────────────────────────────────────────────────────────────


async def test_get_by_ids_multiple(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Находит все conditions по списку id."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    conditions = await make_conditions_with_roles(permission, make_condition, roles)
    ids = [conditions[0].id, conditions[1].id]

    result = await repo.get_by_ids(ids)

    assert len(result) == 2
    assert {c.id for c in result} == set(ids)


async def test_get_by_ids_empty_list(db_session):
    """Пустой список → пустой результат, без запроса в БД."""
    repo = PermissionConditionRepository(db_session)

    result = await repo.get_by_ids([])

    assert result == []


async def test_get_by_ids_unknown_ids(db_session):
    """Несуществующие id не попадают в результат."""
    repo = PermissionConditionRepository(db_session)
    ids = [uuid4(), uuid4()]

    result = await repo.get_by_ids(ids)

    assert result == []


async def test_get_by_ids_mixed_existing_and_unknown(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Смешанные id: существующие возвращаются, несуществующие игнорируются."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    conditions = await make_conditions_with_roles(permission, make_condition, roles)
    existing = conditions[0].id
    ids = [existing, uuid4(), uuid4()]

    result = await repo.get_by_ids(ids)

    assert len(result) == 1
    assert result[0].id == existing


async def test_get_by_ids_duplicates(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Дубликаты в списке → condition возвращается один раз."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    conditions = await make_conditions_with_roles(permission, make_condition, roles)
    existing = conditions[0].id
    ids = [existing, existing, existing]

    result = await repo.get_by_ids(ids)

    assert len(result) == 1
    assert result[0].id == existing


# ─────────────────────────────────────────────────────────────────────
# deactivate_by_ids
# ─────────────────────────────────────────────────────────────────────


async def test_deactivate_by_ids_deactivates_active(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Деактивирует активные conditions."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    conditions = await make_conditions_with_roles(permission, make_condition, roles)
    ids = [conditions[0].id, conditions[1].id]

    rowcount = await repo.deactivate_by_ids(ids)

    assert rowcount == 2
    result = await repo.get_by_ids(ids)
    assert all(c.is_active is False for c in result)


async def test_deactivate_by_ids_skips_already_inactive(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Уже неактивные не считаются в rowcount."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    conditions = await make_conditions_with_roles(permission, make_condition, roles)
    target = conditions[0].id
    await repo.deactivate_by_ids([target])

    rowcount = await repo.deactivate_by_ids([target])

    assert rowcount == 0


async def test_deactivate_by_ids_empty_list(db_session):
    """Пустой список → 0, без запроса в БД."""
    repo = PermissionConditionRepository(db_session)

    rowcount = await repo.deactivate_by_ids([])

    assert rowcount == 0


async def test_deactivate_by_ids_unknown_ids(db_session):
    """Несуществующие id → 0."""
    repo = PermissionConditionRepository(db_session)
    ids = [uuid4(), uuid4()]

    rowcount = await repo.deactivate_by_ids(ids)

    assert rowcount == 0


async def test_deactivate_by_ids_mixed(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Смешанные id: rowcount = число реально изменённых (только активные)."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    conditions = await make_conditions_with_roles(permission, make_condition, roles)
    active = conditions[0].id
    already_inactive = conditions[1].id
    await repo.deactivate_by_ids([already_inactive])

    rowcount = await repo.deactivate_by_ids([active, already_inactive, uuid4()])

    assert rowcount == 1


# ─────────────────────────────────────────────────────────────────────
# activate_by_ids
# ─────────────────────────────────────────────────────────────────────


async def test_activate_by_ids_activates_inactive(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Активирует неактивные conditions."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    conditions = await make_conditions_with_roles(permission, make_condition, roles)
    ids = [conditions[0].id, conditions[1].id]
    await repo.deactivate_by_ids(ids)

    rowcount = await repo.activate_by_ids(ids)

    assert rowcount == 2
    result = await repo.get_by_ids(ids)
    assert all(c.is_active is True for c in result)


async def test_activate_by_ids_skips_already_active(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Уже активные не считаются в rowcount."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    conditions = await make_conditions_with_roles(permission, make_condition, roles)
    target = conditions[0].id

    rowcount = await repo.activate_by_ids([target])

    assert rowcount == 0


async def test_activate_by_ids_empty_list(db_session):
    """Пустой список → 0, без запроса в БД."""
    repo = PermissionConditionRepository(db_session)

    rowcount = await repo.activate_by_ids([])

    assert rowcount == 0


async def test_activate_by_ids_unknown_ids(db_session):
    """Несуществующие id → 0."""
    repo = PermissionConditionRepository(db_session)
    ids = [uuid4(), uuid4()]

    rowcount = await repo.activate_by_ids(ids)

    assert rowcount == 0


async def test_activate_by_ids_mixed(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Смешанные id: rowcount = число реально изменённых (только неактивные)."""
    repo = PermissionConditionRepository(db_session)
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    conditions = await make_conditions_with_roles(permission, make_condition, roles)
    inactive = conditions[0].id
    already_active = conditions[1].id
    await repo.deactivate_by_ids([inactive])

    rowcount = await repo.activate_by_ids([inactive, already_active, uuid4()])

    assert rowcount == 1


# ─────────────────────────────────────────────────────────────────────
# get_by_role
# ─────────────────────────────────────────────────────────────────────


async def test_get_by_role_returns_only_matching(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """Возвращает conditions только указанной роли."""
    target, other = roles[0], roles[1]
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    c1 = await make_condition(permission, type_=ConditionType.ROLE, role_id=target.id)
    c2 = await make_condition(permission, type_=ConditionType.ROLE, role_id=target.id)
    await make_condition(permission, type_=ConditionType.ROLE, role_id=other.id)
    repo = PermissionConditionRepository(db_session)

    result = await repo.get_by_role(target.id)

    assert {c.id for c in result} == {c1.id, c2.id}
    assert all(c.role_id == target.id and c.type == ConditionType.ROLE for c in result)


async def test_get_by_role_unknown_id(db_session):
    """Unknown id -> empty list."""
    repo = PermissionConditionRepository(db_session)

    assert await repo.get_by_role(uuid4()) == []


async def test_get_by_role_filter_is_active(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """is_active фильтр оставляет только подходящие conditions."""
    target = roles[0]
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    active = await make_condition(permission, type_=ConditionType.ROLE, role_id=target.id)
    inactive = await make_condition(
        permission,
        type_=ConditionType.ROLE,
        role_id=target.id,
        is_active=False,
    )
    repo = PermissionConditionRepository(db_session)

    result = await repo.get_by_role(target.id, is_active=True)

    assert [c.id for c in result] == [active.id]
    assert inactive.id not in {c.id for c in result}


# ─────────────────────────────────────────────────────────────────────
# get_by_permission — фильтр по типу
# ─────────────────────────────────────────────────────────────────────


async def test_get_by_permission_filter_condition_type_role(
    db_session,
    make_permission,
    make_condition,
    roles: list[Role],
):
    """condition_type=ROLE returns only ROLE conditions."""
    permission = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
    )
    await make_condition(permission, type_=ConditionType.ALL)
    await make_condition(permission, type_=ConditionType.SUBTREE)
    role_condition = await make_condition(
        permission,
        type_=ConditionType.ROLE,
        role_id=roles[0].id,
    )
    repo = PermissionConditionRepository(db_session)

    result = await repo.get_by_permission(permission.id, condition_type=ConditionType.ROLE)

    assert [c.id for c in result] == [role_condition.id]
    assert result[0].role_id == roles[0].id
