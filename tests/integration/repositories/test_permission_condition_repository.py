"""Tests for PermissionConditionRepository."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import UUID

from app.models.system import ConditionType, PermissionEffect
from app.repositories.system.permission_condition import PermissionConditionRepository

# ─────────────────────────────────────────────────────────────────────
# get_by_permission
# ─────────────────────────────────────────────────────────────────────


async def test_get_by_permission_returns_all_conditions(
    db_session, permissions, permission_conditions_allow, permission_conditions_deny
):
    """Возвращает все conditions для permission'а: ALLOW и DENY."""
    repo = PermissionConditionRepository(db_session)
    target = permissions[0]

    result = await repo.get_by_permission(target.id)

    assert len(result) == 4
    assert {c.effect for c in result} == {PermissionEffect.ALLOW, PermissionEffect.DENY}
    assert all(c.permission_id == target.id for c in result)


async def test_get_by_permission_empty_for_unknown(
    db_session, permissions, permission_conditions_allow
):
    """Возвращает пустой список для permission'а без conditions."""
    repo = PermissionConditionRepository(db_session)
    unknown_id = uuid4()

    result = await repo.get_by_permission(unknown_id)

    assert result == []


async def test_get_by_permission_filter_is_active_true(
    db_session, permissions, permission_conditions_allow
):
    """Фильтр is_active=True возвращает только активные."""
    repo = PermissionConditionRepository(db_session)
    target = permissions[0]

    result = await repo.get_by_permission(target.id, is_active=True)

    assert len(result) == 3
    assert result[0].is_active is True


async def test_get_by_permission_filter_is_active_false(
    db_session, permissions, permission_conditions_allow
):
    """Фильтр is_active=False возвращает только неактивные."""
    repo = PermissionConditionRepository(db_session)
    target = permissions[0]
    await repo.deactivate_by_ids([permission_conditions_allow[0].id])

    result = await repo.get_by_permission(target.id, is_active=False)

    assert len(result) == 1
    assert result[0].is_active is False


async def test_get_by_permission_filter_effect_allow(
    db_session, permissions, permission_conditions_allow, permission_conditions_deny
):
    """Фильтр effect=ALLOW возвращает только ALLOW."""
    repo = PermissionConditionRepository(db_session)
    target = permissions[0]

    result = await repo.get_by_permission(target.id, effect=PermissionEffect.ALLOW)

    assert len(result) == 3
    assert result[0].effect == PermissionEffect.ALLOW


async def test_get_by_permission_filter_effect_deny(
    db_session, permissions, permission_conditions_allow, permission_conditions_deny
):
    """Фильтр effect=DENY возвращает только DENY."""
    repo = PermissionConditionRepository(db_session)
    target = permissions[0]

    result = await repo.get_by_permission(target.id, effect=PermissionEffect.DENY)

    assert len(result) == 1
    assert result[0].effect == PermissionEffect.DENY


async def test_get_by_permission_filter_condition_type_subtree(
    db_session, permissions, permission_conditions_allow, permission_conditions_deny
):
    """Фильтр condition_type=SUBTREE возвращает только SUBTREE."""
    repo = PermissionConditionRepository(db_session)
    target = permissions[1]

    result = await repo.get_by_permission(target.id, condition_type=ConditionType.SUBTREE)

    assert len(result) == 1
    assert result[0].type == ConditionType.SUBTREE


async def test_get_by_permission_filter_condition_type_all(
    db_session, permissions, permission_conditions_allow, permission_conditions_deny
):
    """Фильтр condition_type=ALL возвращает только ALL."""
    repo = PermissionConditionRepository(db_session)
    target = permissions[0]

    result = await repo.get_by_permission(target.id, condition_type=ConditionType.ALL)

    assert len(result) == 1
    assert result[0].type == ConditionType.ALL


async def test_get_by_permission_filter_combination(
    db_session, permissions, permission_conditions_allow, permission_conditions_deny
):
    """Комбинация фильтров is_active=True + effect=ALLOW."""
    repo = PermissionConditionRepository(db_session)
    target = permissions[0]

    result = await repo.get_by_permission(target.id, is_active=True, effect=PermissionEffect.ALLOW)

    assert len(result) == 3
    assert result[0].is_active is True
    assert result[0].effect == PermissionEffect.ALLOW


# ─────────────────────────────────────────────────────────────────────
# get_by_ids
# ─────────────────────────────────────────────────────────────────────


async def test_get_by_ids_multiple(
    db_session, permissions, permission_conditions_allow, permission_conditions_deny
):
    """Находит все conditions по списку id."""
    repo = PermissionConditionRepository(db_session)
    ids = [permission_conditions_allow[0].id, permission_conditions_deny[0].id]

    result = await repo.get_by_ids(ids)

    assert len(result) == 2
    assert {c.id for c in result} == set(ids)


async def test_get_by_ids_empty_list(db_session):
    """Пустой список → пустой результат, без запроса в БД."""
    repo = PermissionConditionRepository(db_session)

    result = await repo.get_by_ids([])

    assert result == []


async def test_get_by_ids_unknown_ids(db_session, permissions, permission_conditions_allow):
    """Несуществующие id не попадают в результат."""
    repo = PermissionConditionRepository(db_session)
    ids = [uuid4(), uuid4()]

    result = await repo.get_by_ids(ids)

    assert result == []


async def test_get_by_ids_mixed_existing_and_unknown(
    db_session, permissions, permission_conditions_allow
):
    """Смешанные id: существующие возвращаются, несуществующие игнорируются."""
    repo = PermissionConditionRepository(db_session)
    existing = permission_conditions_allow[0].id
    ids = [existing, uuid4(), uuid4()]

    result = await repo.get_by_ids(ids)

    assert len(result) == 1
    assert result[0].id == existing


async def test_get_by_ids_duplicates(db_session, permissions, permission_conditions_allow):
    """Дубликаты в списке → condition возвращается один раз."""
    repo = PermissionConditionRepository(db_session)
    existing = permission_conditions_allow[0].id
    ids = [existing, existing, existing]

    result = await repo.get_by_ids(ids)

    assert len(result) == 1
    assert result[0].id == existing


# ─────────────────────────────────────────────────────────────────────
# deactivate_by_ids
# ─────────────────────────────────────────────────────────────────────


async def test_deactivate_by_ids_deactivates_active(
    db_session, permissions, permission_conditions_allow
):
    """Деактивирует активные conditions."""
    repo = PermissionConditionRepository(db_session)
    ids = [permission_conditions_allow[0].id, permission_conditions_allow[1].id]

    rowcount = await repo.deactivate_by_ids(ids)

    assert rowcount == 2
    result = await repo.get_by_ids(ids)
    assert all(c.is_active is False for c in result)


async def test_deactivate_by_ids_skips_already_inactive(
    db_session, permissions, permission_conditions_allow
):
    """Уже неактивные не считаются в rowcount."""
    repo = PermissionConditionRepository(db_session)
    target = permission_conditions_allow[0].id
    await repo.deactivate_by_ids([target])

    rowcount = await repo.deactivate_by_ids([target])

    assert rowcount == 0


async def test_deactivate_by_ids_empty_list(db_session):
    """Пустой список → 0, без запроса в БД."""
    repo = PermissionConditionRepository(db_session)

    rowcount = await repo.deactivate_by_ids([])

    assert rowcount == 0


async def test_deactivate_by_ids_unknown_ids(db_session, permissions, permission_conditions_allow):
    """Несуществующие id → 0."""
    repo = PermissionConditionRepository(db_session)
    ids = [uuid4(), uuid4()]

    rowcount = await repo.deactivate_by_ids(ids)

    assert rowcount == 0


async def test_deactivate_by_ids_mixed(db_session, permissions, permission_conditions_allow):
    """Смешанные id: rowcount = число реально изменённых (только активные)."""
    repo = PermissionConditionRepository(db_session)
    active = permission_conditions_allow[0].id
    already_inactive = permission_conditions_allow[1].id
    await repo.deactivate_by_ids([already_inactive])

    rowcount = await repo.deactivate_by_ids([active, already_inactive, uuid4()])

    assert rowcount == 1


# ─────────────────────────────────────────────────────────────────────
# activate_by_ids
# ─────────────────────────────────────────────────────────────────────


async def test_activate_by_ids_activates_inactive(
    db_session, permissions, permission_conditions_allow
):
    """Активирует неактивные conditions."""
    repo = PermissionConditionRepository(db_session)
    ids = [permission_conditions_allow[0].id, permission_conditions_allow[1].id]
    await repo.deactivate_by_ids(ids)

    rowcount = await repo.activate_by_ids(ids)

    assert rowcount == 2
    result = await repo.get_by_ids(ids)
    assert all(c.is_active is True for c in result)


async def test_activate_by_ids_skips_already_active(
    db_session, permissions, permission_conditions_allow
):
    """Уже активные не считаются в rowcount."""
    repo = PermissionConditionRepository(db_session)
    target = permission_conditions_allow[0].id

    rowcount = await repo.activate_by_ids([target])

    assert rowcount == 0


async def test_activate_by_ids_empty_list(db_session):
    """Пустой список → 0, без запроса в БД."""
    repo = PermissionConditionRepository(db_session)

    rowcount = await repo.activate_by_ids([])

    assert rowcount == 0


async def test_activate_by_ids_unknown_ids(db_session, permissions, permission_conditions_allow):
    """Несуществующие id → 0."""
    repo = PermissionConditionRepository(db_session)
    ids = [uuid4(), uuid4()]

    rowcount = await repo.activate_by_ids(ids)

    assert rowcount == 0


async def test_activate_by_ids_mixed(db_session, permissions, permission_conditions_allow):
    """Смешанные id: rowcount = число реально изменённых (только неактивные)."""
    repo = PermissionConditionRepository(db_session)
    inactive = permission_conditions_allow[0].id
    already_active = permission_conditions_allow[1].id
    await repo.deactivate_by_ids([inactive])

    rowcount = await repo.activate_by_ids([inactive, already_active, uuid4()])

    assert rowcount == 1


@pytest_asyncio.fixture(params=["role"])
async def scope(request, user, make_role) -> SimpleNamespace:
    """Describes one of get_by_role .

    Описывает один из методов get_by_role /  get_by_media_type.
    """

    async def new_role() -> UUID:
        return (await make_role(name=f"Role {uuid4().hex}", owner_id=user.id)).id

    spec = {
        "role": (ConditionType.ROLE, "get_by_role", "role_id", new_role),
    }
    type_, method, field, factory = spec[request.param]
    return SimpleNamespace(type=type_, method=method, field=field, new_target=factory)


async def test_get_by_scope_returns_only_matching(db_session, permissions, make_condition, scope):
    """Returns conditions of the requested role/media type only.

    Возвращает условия только указанной роли /  типа медиа.
    """
    target, other = await scope.new_target(), await scope.new_target()
    c1 = await make_condition(permissions[0], type_=scope.type, **{scope.field: target})
    c2 = await make_condition(permissions[1], type_=scope.type, **{scope.field: target})
    await make_condition(permissions[0], type_=scope.type, **{scope.field: other})
    repo = PermissionConditionRepository(db_session)

    result = await getattr(repo, scope.method)(target)

    assert {c.id for c in result} == {c1.id, c2.id}
    assert all(getattr(c, scope.field) == target and c.type == scope.type for c in result)
    assert {c.permission_id for c in result} == {permissions[0].id, permissions[1].id}


async def test_get_by_scope_unknown_id(db_session, scope):
    """Unknown id -> empty list.

    Неизвестный id -> пустой список.
    """
    repo = PermissionConditionRepository(db_session)

    assert await getattr(repo, scope.method)(uuid4()) == []


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        pytest.param({}, {"allow", "deny", "inactive"}, id="no_filters"),
        pytest.param({"is_active": True}, {"allow", "deny"}, id="active"),
        pytest.param({"is_active": False}, {"inactive"}, id="inactive"),
        pytest.param({"effect": PermissionEffect.DENY}, {"deny"}, id="deny"),
        pytest.param(
            {"is_active": True, "effect": PermissionEffect.ALLOW}, {"allow"}, id="active_allow"
        ),
    ],
)
async def test_get_by_scope_filters(
    db_session, permissions, make_condition, scope, filters, expected
):
    """is_active / effect filters, alone and combined.

    Фильтры is_active / effect по отдельности и вместе.
    """
    target = await scope.new_target()
    kw = {scope.field: target}
    created = {
        "allow": await make_condition(permissions[0], type_=scope.type, **kw),
        "deny": await make_condition(
            permissions[0], type_=scope.type, effect=PermissionEffect.DENY, **kw
        ),
        "inactive": await make_condition(permissions[1], type_=scope.type, is_active=False, **kw),
    }
    repo = PermissionConditionRepository(db_session)

    result = await getattr(repo, scope.method)(target, **filters)

    assert {c.id for c in result} == {created[name].id for name in expected}


async def test_get_by_permission_filter_condition_type_role(
    db_session, permissions, role, make_condition
):
    """condition_type=ROLE returns only ROLE conditions.

    condition_type=ROLE возвращает только ROLE-условия.
    """
    target = permissions[0]
    await make_condition(target, type_=ConditionType.ALL)
    await make_condition(target, type_=ConditionType.SUBTREE)
    role_condition = await make_condition(target, type_=ConditionType.ROLE, role_id=role.id)
    repo = PermissionConditionRepository(db_session)

    result = await repo.get_by_permission(target.id, condition_type=ConditionType.ROLE)

    assert [c.id for c in result] == [role_condition.id]
    assert result[0].role_id == role.id


async def test_get_by_permission_filter_effect_and_type(db_session, permissions, make_condition):
    """effect + condition_type combine with AND.

    effect + condition_type объединяются через AND.
    """
    target = permissions[0]
    await make_condition(target, type_=ConditionType.ALL, effect=PermissionEffect.ALLOW)
    wanted = await make_condition(target, type_=ConditionType.ALL, effect=PermissionEffect.DENY)
    await make_condition(target, type_=ConditionType.SUBTREE, effect=PermissionEffect.DENY)
    repo = PermissionConditionRepository(db_session)

    result = await repo.get_by_permission(
        target.id, effect=PermissionEffect.DENY, condition_type=ConditionType.ALL
    )

    assert [c.id for c in result] == [wanted.id]
