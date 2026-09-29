"""Tests for RolePermissionRepository."""

from app.repositories.system.role_permission import RolePermissionRepository

# ─────────────────────────────────────────────────────────────
# get_condition_ids_by_role_id
# ─────────────────────────────────────────────────────────────


async def test_get_condition_ids_by_role_id(
    db_session, role, permission_conditions_allow, role_permissions
):
    """Возвращает все condition_id роли."""
    repo = RolePermissionRepository(db_session)

    result = await repo.get_condition_ids_by_role_id(role.id)

    expected = {c.id for c in permission_conditions_allow}
    assert set(result) == expected


async def test_get_condition_ids_by_role_id_empty(db_session, role):
    """Пустой список, если у роли нет conditions."""
    repo = RolePermissionRepository(db_session)

    result = await repo.get_condition_ids_by_role_id(role.id)

    assert result == []


async def test_get_condition_ids_by_role_id_isolated(
    db_session, roles, permission_conditions_allow, make_role_permission
):
    """Conditions другой роли не попадают."""
    role_a, role_b = roles[0], roles[1]
    await make_role_permission(role_a, permission_conditions_allow[0])
    await make_role_permission(role_b, permission_conditions_allow[1])
    repo = RolePermissionRepository(db_session)

    result = await repo.get_condition_ids_by_role_id(role_a.id)

    assert result == [permission_conditions_allow[0].id]


# ─────────────────────────────────────────────────────────────
# get_role_ids_by_condition_id
# ─────────────────────────────────────────────────────────────


async def test_get_role_ids_by_condition_id(
    db_session, roles, permission_conditions_allow, make_role_permission
):
    """Возвращает все role_id для condition."""
    condition = permission_conditions_allow[0]
    for role in roles:
        await make_role_permission(role, condition)
    repo = RolePermissionRepository(db_session)

    result = await repo.get_role_ids_by_condition_id(condition.id)

    expected = {r.id for r in roles}
    assert set(result) == expected


async def test_get_role_ids_by_condition_id_empty(db_session, permission_conditions_allow):
    """Пустой список, если condition нет ни у одной роли."""
    repo = RolePermissionRepository(db_session)

    result = await repo.get_role_ids_by_condition_id(permission_conditions_allow[0].id)

    assert result == []


async def test_get_role_ids_by_condition_id_isolated(
    db_session, roles, permission_conditions_allow, make_role_permission
):
    """Roles для другой condition не попадают."""
    role_a, role_b = roles[0], roles[1]
    await make_role_permission(role_a, permission_conditions_allow[0])
    await make_role_permission(role_b, permission_conditions_allow[1])
    repo = RolePermissionRepository(db_session)

    result = await repo.get_role_ids_by_condition_id(permission_conditions_allow[0].id)

    assert result == [role_a.id]
