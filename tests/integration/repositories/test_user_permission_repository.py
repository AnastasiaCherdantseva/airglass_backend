"""Tests for UserPermissionRepository."""

from uuid import uuid4

from app.models.system import ConditionType, PermissionEffect
from app.repositories.system.user_permission import UserPermissionRepository

# ─────────────────────────────────────────────────────────────
# get_grouped_by_permission
# ─────────────────────────────────────────────────────────────


async def test_get_grouped_empty(db_session, user):
    """Пустой результат, если у юзера нет связей."""
    repo = UserPermissionRepository(db_session)

    result = await repo.get_grouped_by_permission(user.id)

    assert result == []


async def test_get_grouped_one_condition(
    db_session, user, user_permission, permission_conditions_allow
):
    """Одна связь → одна GroupedPermission с одной condition."""
    repo = UserPermissionRepository(db_session)

    result = await repo.get_grouped_by_permission(user.id)

    assert len(result) == 1
    assert result[0].code is not None
    assert len(result[0].conditions) == 1
    assert result[0].conditions[0].effect == "allow"


async def test_get_grouped_metadata(
    db_session, user, user_permission, permissions, permission_conditions_allow
):
    """Метаданные GroupedPermission: permission_id, code."""
    repo = UserPermissionRepository(db_session)

    result = await repo.get_grouped_by_permission(user.id)

    assert result[0].permission_id == permission_conditions_allow[0].permission_id
    target = next(p for p in permissions if p.id == result[0].permission_id)
    assert result[0].code == target.code


async def test_get_grouped_conditions_are_full_dto(
    db_session, user, user_permission, permission_conditions_allow
):
    """conditions[] — полные PermissionConditionAllOutPut."""
    repo = UserPermissionRepository(db_session)

    result = await repo.get_grouped_by_permission(user.id)

    condition = result[0].conditions[0]
    source = permission_conditions_allow[0]
    assert condition.id == source.id
    assert condition.permission_id == source.permission_id
    assert condition.type == source.type
    assert condition.effect == source.effect
    assert condition.is_active == source.is_active


async def test_get_grouped_multiple_conditions_same_permission(
    db_session, user, permissions, make_condition, make_user_permission
):
    """Несколько conditions для одного permission → одна группа."""
    permission = permissions[0]
    c1 = await make_condition(permission, type_=ConditionType.ALL, effect=PermissionEffect.ALLOW)
    c2 = await make_condition(permission, type_=ConditionType.SUBTREE, effect=PermissionEffect.DENY)
    await make_user_permission(user, c1)
    await make_user_permission(user, c2)

    repo = UserPermissionRepository(db_session)
    result = await repo.get_grouped_by_permission(user.id)

    assert len(result) == 1
    assert len(result[0].conditions) == 2


async def test_get_grouped_multiple_permissions(
    db_session, user, permissions, make_condition, make_user_permission
):
    """Разные permissions → разные группы."""
    c1 = await make_condition(permissions[0], type_=ConditionType.ALL)
    c2 = await make_condition(permissions[1], type_=ConditionType.ALL)
    await make_user_permission(user, c1)
    await make_user_permission(user, c2)

    repo = UserPermissionRepository(db_session)
    result = await repo.get_grouped_by_permission(user.id)

    assert len(result) == 2
    permission_ids = {g.permission_id for g in result}
    assert permission_ids == {permissions[0].id, permissions[1].id}


async def test_get_grouped_isolated_by_user(
    db_session, users, permissions, make_condition, make_user_permission
):
    """Связи другого юзера не попадают в результат."""
    c1 = await make_condition(permissions[0], type_=ConditionType.ALL)
    await make_user_permission(users[0], c1)
    await make_user_permission(users[1], c1)

    repo = UserPermissionRepository(db_session)
    result = await repo.get_grouped_by_permission(users[0].id)

    assert len(result) == 1


# ─────────────────────────────────────────────────────────────
# replace_for_user
# ─────────────────────────────────────────────────────────────


async def test_replace_from_empty_to_filled(db_session, user, permissions, make_condition):
    """Заполняет с нуля."""
    c1 = await make_condition(permissions[0], type_=ConditionType.ALL)
    c2 = await make_condition(permissions[1], type_=ConditionType.ALL)
    repo = UserPermissionRepository(db_session)

    await repo.replace_for_user(user.id, [c1.id, c2.id])

    result = await repo.get_grouped_by_permission(user.id)
    assert len(result) == 2


async def test_replace_removes_old(
    db_session, user, permissions, make_condition, make_user_permission
):
    """Старые связи удаляются, новые вставляются."""
    old = await make_condition(permissions[0], type_=ConditionType.ALL)
    new = await make_condition(permissions[1], type_=ConditionType.ALL)
    await make_user_permission(user, old)
    repo = UserPermissionRepository(db_session)

    await repo.replace_for_user(user.id, [new.id])

    result = await repo.get_grouped_by_permission(user.id)
    assert len(result) == 1
    assert result[0].permission_id == permissions[1].id


async def test_replace_with_empty_list_clears(
    db_session, user, permissions, make_condition, make_user_permission
):
    """Пустой список → всё удалено."""
    c1 = await make_condition(permissions[0], type_=ConditionType.ALL)
    await make_user_permission(user, c1)
    repo = UserPermissionRepository(db_session)

    await repo.replace_for_user(user.id, [])

    result = await repo.get_grouped_by_permission(user.id)
    assert result == []


async def test_replace_does_not_touch_other_users(
    db_session, users, permissions, make_condition, make_user_permission
):
    """Связи другого юзера не трогаются."""
    c1 = await make_condition(permissions[0], type_=ConditionType.ALL)
    c2 = await make_condition(permissions[1], type_=ConditionType.ALL)
    await make_user_permission(users[1], c2)
    repo = UserPermissionRepository(db_session)

    await repo.replace_for_user(users[0].id, [c1.id])

    other = await repo.get_grouped_by_permission(users[1].id)
    assert len(other) == 1
    assert other[0].permission_id == permissions[1].id


# ─────────────────────────────────────────────────────────────
# delete_by_user_id
# ─────────────────────────────────────────────────────────────


async def test_delete_by_user_id_removes_all(db_session, user, user_permissions):
    """Удаляет все связи юзера, возвращает rowcount."""
    repo = UserPermissionRepository(db_session)
    expected = len(user_permissions)

    rowcount = await repo.delete_by_user_id(user.id)

    assert rowcount == expected
    result = await repo.get_grouped_by_permission(user.id)
    assert result == []


async def test_delete_by_user_id_unknown(db_session, user):
    """Несуществующий юзер → 0."""
    repo = UserPermissionRepository(db_session)

    rowcount = await repo.delete_by_user_id(uuid4())

    assert rowcount == 0


async def test_delete_by_user_id_does_not_touch_others(
    db_session, users, permissions, make_condition, make_user_permission
):
    """Связи других юзеров не трогаются."""
    c1 = await make_condition(permissions[0], type_=ConditionType.ALL)
    await make_user_permission(users[0], c1)
    await make_user_permission(users[1], c1)
    repo = UserPermissionRepository(db_session)

    await repo.delete_by_user_id(users[0].id)

    other = await repo.get_grouped_by_permission(users[1].id)
    assert len(other) == 1
