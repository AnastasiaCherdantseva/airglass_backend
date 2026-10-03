"""Tests for UserRoleRepository."""

from uuid import uuid4

from app.repositories.system.user_role import UserRoleRepository

# ─────────────────────────────────────────────────────────────
# get_roles_by_user_id
# ─────────────────────────────────────────────────────────────


async def test_get_roles_by_user_id_returns_roles(db_session, user, system_roles, user_roles):
    """Возвращает роли, привязанные к юзеру."""
    repo = UserRoleRepository(db_session)

    result = await repo.get_roles_by_user_id(user.id)

    assert len(result) == 3
    role_ids = {r.id for r in result}
    assert role_ids == {r.id for r in system_roles}


async def test_get_roles_by_user_id_empty(db_session, user):
    """Пустой список, если юзер не привязан ни к одной роли."""
    repo = UserRoleRepository(db_session)

    result = await repo.get_roles_by_user_id(user.id)

    assert result == []


async def test_get_roles_by_user_id_filters_inactive(db_session, user, make_role, make_user_role):
    """Неактивные роли не возвращаются."""
    active = await make_role(name="Активная", owner_id=None, is_active=True, is_system=True)
    inactive = await make_role(name="Неактивная", owner_id=None, is_active=False, is_system=True)
    await make_user_role(user, active)
    await make_user_role(user, inactive)
    repo = UserRoleRepository(db_session)

    result = await repo.get_roles_by_user_id(user.id)

    assert len(result) == 1
    assert result[0].id == active.id


async def test_get_roles_by_user_id_isolated(db_session, users, system_role, make_user_role):
    """Связи роль-второй юзер не попадают в результат для первого юзера."""
    await make_user_role(users[0], system_role)
    await make_user_role(users[1], system_role)
    repo = UserRoleRepository(db_session)

    result = await repo.get_roles_by_user_id(users[0].id)

    assert len(result) == 1
    assert result[0].id == system_role.id


# ─────────────────────────────────────────────────────────────
# get_users_by_role_id
# ─────────────────────────────────────────────────────────────


async def test_get_users_by_role_id_returns_users(db_session, users, system_role, make_user_role):
    """Возвращает юзеров, привязанныхъ к этой роли."""
    await make_user_role(users[0], system_role)
    await make_user_role(users[1], system_role)
    repo = UserRoleRepository(db_session)

    result = await repo.get_users_by_role_id(system_role.id)

    assert len(result) == 2
    user_ids = {u.id for u in result}
    assert user_ids == {users[0].id, users[1].id}


async def test_get_users_by_role_id_empty(db_session, role):
    """Пустой список, если роли ни у кого нет."""
    repo = UserRoleRepository(db_session)

    result = await repo.get_users_by_role_id(role.id)

    assert result == []


async def test_get_users_by_role_id_filters_deleted(db_session, users, system_role, make_user_role):
    """Удалённые юзеры не возвращаются."""
    from datetime import UTC, datetime

    await make_user_role(users[0], system_role)
    await make_user_role(users[1], system_role)
    users[1].deleted_at = datetime.now(UTC)
    await db_session.flush()
    repo = UserRoleRepository(db_session)

    result = await repo.get_users_by_role_id(system_role.id)

    assert len(result) == 1
    assert result[0].id == users[0].id


# ─────────────────────────────────────────────────────────────
# get_user_ids_by_role_id
# ─────────────────────────────────────────────────────────────


async def test_get_user_ids_by_role_id(db_session, users, system_role, make_user_role):
    """ID юзеров ,которые привязаны к роли."""
    await make_user_role(users[0], system_role)
    await make_user_role(users[1], system_role)
    repo = UserRoleRepository(db_session)

    result = await repo.get_user_ids_by_role_id(system_role.id)

    assert set(result) == {users[0].id, users[1].id}


async def test_get_user_ids_by_role_id_empty(db_session, role):
    """Пустой список, если роль ни у кого нет."""
    repo = UserRoleRepository(db_session)

    result = await repo.get_user_ids_by_role_id(role.id)

    assert result == []


# ─────────────────────────────────────────────────────────────
# add_link / remove_link
# ─────────────────────────────────────────────────────────────


async def test_add_link(db_session, user, system_role):
    """add_link создаёт связь."""
    from app.dto.system import UserRoleLink

    repo = UserRoleRepository(db_session)
    data = UserRoleLink(user_id=user.id, role_id=system_role.id)

    await repo.add_link(data)

    roles = await repo.get_roles_by_user_id(user.id)
    assert len(roles) == 1
    assert roles[0].id == system_role.id


async def test_add_links(db_session, user, system_roles):
    """add_link создаёт связь."""
    from app.dto.system import UserRoleLink

    repo = UserRoleRepository(db_session)
    data = []
    for role in system_roles:
        data.append(UserRoleLink(user_id=user.id, role_id=role.id))

    await repo.add_links(data)

    roles = await repo.get_roles_by_user_id(user.id)
    assert len(roles) == len(system_roles)
    role_ids = [role.id for role in roles]
    for role in roles:
        assert role.id in role_ids


async def test_remove_link_found(db_session, user_role, user, system_role):
    """remove_link удаляет связь, возвращает True."""
    from app.dto.system import UserRoleLink

    repo = UserRoleRepository(db_session)
    data = UserRoleLink(user_id=user.id, role_id=system_role.id)

    result = await repo.remove_link(data)

    assert result is True
    roles = await repo.get_roles_by_user_id(user.id)
    assert roles == []


async def test_remove_link_not_found(db_session, user, system_role):
    """remove_link возвращает False, если связи нет."""
    from app.dto.system import UserRoleLink

    repo = UserRoleRepository(db_session)
    data = UserRoleLink(user_id=user.id, role_id=system_role.id)

    result = await repo.remove_link(data)

    assert result is False


async def test_remove_links_found(db_session, user_roles, user, system_roles):
    """remove_link удаляет связь, возвращает True."""
    from app.dto.system import UserRoleLink

    repo = UserRoleRepository(db_session)
    data = []
    for role in system_roles:
        data.append(UserRoleLink(user_id=user.id, role_id=role.id))

    result = await repo.remove_links(data)

    assert result == 3
    roles = await repo.get_roles_by_user_id(user.id)
    assert roles == []


# ─────────────────────────────────────────────────────────────
# remove_by_user_id / remove_by_role_id
# ─────────────────────────────────────────────────────────────


async def test_remove_by_user_id(db_session, user, user_roles):
    """Удаляет все связи с ролью у юзера, возвращает rowcount."""
    repo = UserRoleRepository(db_session)

    rowcount = await repo.remove_by_user_id(user.id)

    assert rowcount == 3
    roles = await repo.get_roles_by_user_id(user.id)
    assert roles == []


async def test_remove_by_user_id_unknown(db_session):
    """Несуществующий юзер → 0."""
    repo = UserRoleRepository(db_session)

    rowcount = await repo.remove_by_user_id(uuid4())

    assert rowcount == 0


async def test_remove_by_role_id(db_session, users, role, make_user_role):
    """Удаляет все связи роли, возвращает rowcount."""
    await make_user_role(users[0], role)
    await make_user_role(users[1], role)
    repo = UserRoleRepository(db_session)

    rowcount = await repo.remove_by_role_id(role.id)

    assert rowcount == 2
    users_result = await repo.get_users_by_role_id(role.id)
    assert users_result == []


async def test_remove_by_role_id_unknown(db_session):
    """Несуществующая роль → 0."""
    repo = UserRoleRepository(db_session)

    rowcount = await repo.remove_by_role_id(uuid4())

    assert rowcount == 0
