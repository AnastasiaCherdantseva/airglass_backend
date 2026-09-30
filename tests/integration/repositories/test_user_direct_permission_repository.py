"""Tests for UserDirectPermissionRepository."""

from app.repositories.system.user_direct_permission import (
    UserDirectPermissionRepository,
)

# ─────────────────────────────────────────────────────────────
# get_condition_ids_by_user_id
# ─────────────────────────────────────────────────────────────


async def test_get_condition_ids_by_user_id(
    db_session, user, permission_conditions_allow, user_direct_permissions
):
    """Возвращает все condition_id пользователя."""
    repo = UserDirectPermissionRepository(db_session)

    result = await repo.get_condition_ids_by_user_id(user.id)

    expected = {c.id for c in permission_conditions_allow}
    assert set(result) == expected


async def test_get_condition_ids_by_user_id_empty(db_session, user):
    """Пустой список, если у юзера нет direct permissions."""
    repo = UserDirectPermissionRepository(db_session)

    result = await repo.get_condition_ids_by_user_id(user.id)

    assert result == []


async def test_get_condition_ids_by_user_id_isolated(
    db_session, users, permission_conditions_allow, make_user_direct_permission
):
    """Direct permissions другого юзера не попадают."""
    user_a, user_b = users[0], users[1]
    await make_user_direct_permission(user_a, permission_conditions_allow[0])
    await make_user_direct_permission(user_b, permission_conditions_allow[1])
    repo = UserDirectPermissionRepository(db_session)

    result = await repo.get_condition_ids_by_user_id(user_a.id)

    assert result == [permission_conditions_allow[0].id]


# ─────────────────────────────────────────────────────────────
# get_user_ids_by_condition_id
# ─────────────────────────────────────────────────────────────


async def test_get_user_ids_by_condition_id(
    db_session, users, permission_conditions_allow, make_user_direct_permission
):
    """Возвращает всех юзеров с этой direct condition."""
    condition = permission_conditions_allow[0]
    await make_user_direct_permission(users[0], condition)
    await make_user_direct_permission(users[1], condition)
    repo = UserDirectPermissionRepository(db_session)

    result = await repo.get_user_ids_by_condition_id(condition.id)

    assert set(result) == {users[0].id, users[1].id}


async def test_get_user_ids_by_condition_id_empty(db_session, permission_conditions_allow):
    """Пустой список, если condition ни у кого нет."""
    repo = UserDirectPermissionRepository(db_session)

    result = await repo.get_user_ids_by_condition_id(permission_conditions_allow[0].id)

    assert result == []


async def test_get_user_ids_by_condition_id_isolated(
    db_session, users, permission_conditions_allow, make_user_direct_permission
):
    """Direct permissions другой condition не попадают."""
    user_a, user_b = users[0], users[1]
    await make_user_direct_permission(user_a, permission_conditions_allow[0])
    await make_user_direct_permission(user_b, permission_conditions_allow[1])
    repo = UserDirectPermissionRepository(db_session)

    result = await repo.get_user_ids_by_condition_id(permission_conditions_allow[0].id)

    assert result == [user_a.id]
