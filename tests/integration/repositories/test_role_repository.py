"""Tests for RoleRepository."""

from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.dto import RoleData, RolePatchData
from app.models.system.user_role import UserRole
from app.repositories.system.role import RoleRepository

# ─────────────────────────────────────────────────────────────
# get_by_owner_id
# ─────────────────────────────────────────────────────────────


async def test_get_by_owner_id_returns_all(db_session, user, roles):
    """Возвращает все роли владельца."""
    repo = RoleRepository(db_session)

    result = await repo.get_by_owner_id(user.id)

    assert len(result) == 3
    assert all(r.owner_id == user.id for r in result)


async def test_get_by_owner_id_empty(db_session, user):
    """Пустой список, если у владельца нет ролей."""
    repo = RoleRepository(db_session)

    result = await repo.get_by_owner_id(user.id)

    assert result == []


async def test_get_by_owner_id_isolated(db_session, users, roles_for_two_users):
    """Роли другого владельца не попадают."""
    repo = RoleRepository(db_session)
    user_a = users[0]

    result = await repo.get_by_owner_id(user_a.id)

    expected_count = len(roles_for_two_users[user_a.id])
    assert len(result) == expected_count
    assert all(r.owner_id == user_a.id for r in result)


async def test_get_by_owner_id_filter_is_active_true(db_session, user, make_role):
    """Фильтр is_active=True — только активные."""
    active = await make_role(name="Активная", owner_id=user.id, is_active=True)
    await make_role(name="Неактивная", owner_id=user.id, is_active=False)
    repo = RoleRepository(db_session)

    result = await repo.get_by_owner_id(user.id, is_active=True)

    assert len(result) == 1
    assert result[0].id == active.id


async def test_get_by_owner_id_filter_is_active_false(db_session, user, make_role):
    """Фильтр is_active=False — только неактивные."""
    await make_role(name="Активная", owner_id=user.id, is_active=True)
    inactive = await make_role(name="Неактивная", owner_id=user.id, is_active=False)
    repo = RoleRepository(db_session)

    result = await repo.get_by_owner_id(user.id, is_active=False)

    assert len(result) == 1
    assert result[0].id == inactive.id


# ─────────────────────────────────────────────────────────────
# create
# ─────────────────────────────────────────────────────────────


async def test_create_role(db_session, user):
    """Создаёт роль и возвращает RoleOutput с id."""
    repo = RoleRepository(db_session)
    data = RoleData(
        name="Новая роль",
        owner_id=user.id,
        description="Описание",
        is_system=False,
        is_active=True,
    )

    result = await repo.create(data)

    assert result.id is not None
    assert result.name == "Новая роль"
    assert result.owner_id == user.id
    assert result.description == "Описание"
    assert result.is_system is False
    assert result.is_active is True

    # Проверка, что роль в БД
    found = await repo.get_by_id(result.id)
    assert found is not None
    assert found.name == "Новая роль"


async def test_create_role_description_none(db_session, user):
    """description=None обрабатывается корректно."""
    repo = RoleRepository(db_session)
    data = RoleData(
        name="Без описания",
        owner_id=user.id,
        description=None,
        is_system=False,
        is_active=True,
    )

    result = await repo.create(data)

    assert result.description is None


# ─────────────────────────────────────────────────────────────
# patch
# ─────────────────────────────────────────────────────────────


async def test_patch_updates_name(db_session, role):
    """patch обновляет name."""
    repo = RoleRepository(db_session)
    data = RolePatchData(
        id=role.id,
        name="Обновлённое имя",
        description=None,
        is_active=None,
    )

    result = await repo.patch(data)

    assert result is not None
    assert result.name == "Обновлённое имя"
    assert result.description == role.description  # не изменилось
    assert result.is_active == role.is_active  # не изменилось


async def test_patch_updates_is_active(db_session, role):
    """patch обновляет is_active."""
    repo = RoleRepository(db_session)
    data = RolePatchData(
        id=role.id,
        name=None,
        description=None,
        is_active=False,
    )

    result = await repo.patch(data)

    assert result is not None
    assert result.is_active is False
    assert result.name == role.name  # не изменилось


async def test_patch_updates_description(db_session, role):
    """patch обновляет description."""
    repo = RoleRepository(db_session)
    data = RolePatchData(
        id=role.id,
        name=None,
        description="Новое описание",
        is_active=None,
    )

    result = await repo.patch(data)

    assert result is not None
    assert result.description == "Новое описание"


async def test_patch_not_found(db_session):
    """patch возвращает None для несуществующей роли."""
    repo = RoleRepository(db_session)
    data = RolePatchData(
        id=uuid4(),
        name="Новое имя",
        description=None,
        is_active=None,
    )

    result = await repo.patch(data)

    assert result is None


# ─────────────────────────────────────────────────────────────
# activate_by_ids / deactivate_by_ids
# ─────────────────────────────────────────────────────────────


async def test_deactivate_by_ids_deactivates_active(db_session, user, make_role):
    """Деактивирует активные роли."""
    r1 = await make_role(name="Роль 1", owner_id=user.id, is_active=True)
    r2 = await make_role(name="Роль 2", owner_id=user.id, is_active=True)
    repo = RoleRepository(db_session)

    rowcount = await repo.deactivate_by_ids([r1.id, r2.id])

    assert rowcount == 2
    found1 = await repo.get_by_id(r1.id)
    found2 = await repo.get_by_id(r2.id)
    assert found1.is_active is False
    assert found2.is_active is False


async def test_deactivate_by_ids_skips_already_inactive(db_session, user, make_role):
    """Уже неактивные не считаются в rowcount."""
    role = await make_role(name="Роль", owner_id=user.id, is_active=False)
    repo = RoleRepository(db_session)

    rowcount = await repo.deactivate_by_ids([role.id])

    assert rowcount == 0


async def test_deactivate_by_ids_empty_list(db_session):
    """Пустой список → 0."""
    repo = RoleRepository(db_session)

    rowcount = await repo.deactivate_by_ids([])

    assert rowcount == 0


async def test_deactivate_by_ids_unknown_ids(db_session):
    """Несуществующие id → 0."""
    repo = RoleRepository(db_session)

    rowcount = await repo.deactivate_by_ids([uuid4(), uuid4()])

    assert rowcount == 0


async def test_deactivate_by_ids_mixed(db_session, user, make_role):
    """Смешанные: rowcount = только активные."""
    active = await make_role(name="Активная", owner_id=user.id, is_active=True)
    inactive = await make_role(name="Неактивная", owner_id=user.id, is_active=False)
    repo = RoleRepository(db_session)

    rowcount = await repo.deactivate_by_ids([active.id, inactive.id, uuid4()])

    assert rowcount == 1


async def test_activate_by_ids_activates_inactive(db_session, user, make_role):
    """Активирует неактивные роли."""
    r1 = await make_role(name="Роль 1", owner_id=user.id, is_active=False)
    r2 = await make_role(name="Роль 2", owner_id=user.id, is_active=False)
    repo = RoleRepository(db_session)

    rowcount = await repo.activate_by_ids([r1.id, r2.id])

    assert rowcount == 2
    found1 = await repo.get_by_id(r1.id)
    found2 = await repo.get_by_id(r2.id)
    assert found1.is_active is True
    assert found2.is_active is True


async def test_activate_by_ids_skips_already_active(db_session, user, make_role):
    """Уже активные не считаются в rowcount."""
    role = await make_role(name="Роль", owner_id=user.id, is_active=True)
    repo = RoleRepository(db_session)

    rowcount = await repo.activate_by_ids([role.id])

    assert rowcount == 0


async def test_activate_by_ids_empty_list(db_session):
    """Пустой список → 0."""
    repo = RoleRepository(db_session)

    rowcount = await repo.activate_by_ids([])

    assert rowcount == 0


async def test_activate_by_ids_mixed(db_session, user, make_role):
    """Смешанные: rowcount = только неактивные."""
    inactive = await make_role(name="Неактивная", owner_id=user.id, is_active=False)
    active = await make_role(name="Активная", owner_id=user.id, is_active=True)
    repo = RoleRepository(db_session)

    rowcount = await repo.activate_by_ids([inactive.id, active.id, uuid4()])

    assert rowcount == 1


async def test_get_by_ids_returns_found_and_ignores_unknown(db_session, roles):
    """Existing ids are returned, unknown ones are ignored.

    Существующие id возвращаются, неизвестные игнорируются.
    """
    repo = RoleRepository(db_session)

    result = await repo.get_by_ids([roles[0].id, roles[1].id, uuid4()])

    assert {r.id for r in result} == {roles[0].id, roles[1].id}


async def test_get_by_ids_empty_list(db_session):
    """Empty list -> empty result.

    Пустой список -> пустой результат.
    """
    assert await RoleRepository(db_session).get_by_ids([]) == []


async def test_get_ids_by_owner_ids_several_owners(db_session, users, make_role):
    """Returns roles of all given owners and no others.

    Возвращает роли всех указанных владельцев и только их.
    """
    ra = [await make_role(name=f"A{i}", owner_id=users[0].id) for i in range(2)]
    rb = await make_role(name="B", owner_id=users[1].id)
    await make_role(name="C", owner_id=users[2].id)
    repo = RoleRepository(db_session)

    result = await repo.get_ids_by_owner_ids([users[0].id, users[1].id])

    assert {r.id for r in result} == {ra[0].id, ra[1].id, rb.id}


@pytest.mark.parametrize("is_active", [True, False])
async def test_get_ids_by_owner_ids_filter_is_active(db_session, users, make_role, is_active):
    """is_active filter keeps only matching roles.

    Фильтр is_active оставляет только подходящие роли.
    """
    active = await make_role(name="Активная", owner_id=users[0].id, is_active=True)
    inactive = await make_role(name="Неактивная", owner_id=users[0].id, is_active=False)
    repo = RoleRepository(db_session)

    result = await repo.get_ids_by_owner_ids([users[0].id], is_active=is_active)

    assert [r.id for r in result] == [(active if is_active else inactive).id]


async def test_get_ids_by_owner_ids_empty_list(db_session):
    """Empty list -> empty result.

    Пустой список -> пустой результат.
    """
    assert await RoleRepository(db_session).get_ids_by_owner_ids([]) == []


async def test_delete_by_owner_ids(db_session, users, make_role):
    """Deletes roles of several owners, returns rowcount, keeps other owners.

    Удаляет роли нескольких владельцев, возвращает rowcount, чужие роли остаются.
    """
    doomed = [
        await make_role(name="A1", owner_id=users[0].id),
        await make_role(name="A2", owner_id=users[0].id),
        await make_role(name="B", owner_id=users[1].id),
    ]
    kept = await make_role(name="C", owner_id=users[2].id)
    repo = RoleRepository(db_session)

    rowcount = await repo.delete_by_owner_ids([users[0].id, users[1].id])

    assert rowcount == 3
    for role in doomed:
        assert await repo.get_by_id(role.id) is None
    assert await repo.get_by_id(kept.id) is not None


async def test_delete_by_owner_ids_empty_and_unknown(db_session):
    """Empty list and unknown owners -> 0.

    Пустой список и неизвестные владельцы -> 0.
    """
    repo = RoleRepository(db_session)

    assert await repo.delete_by_owner_ids([]) == 0
    assert await repo.delete_by_owner_ids([uuid4()]) == 0


async def test_delete_by_owner_ids_cascades_user_roles(
    db_session, users, make_role, make_user_role
):
    """Links user<->role of the deleted roles disappear (ondelete CASCADE).

    Связи user<->role удалённых ролей исчезают (ondelete CASCADE).
    """
    role = await make_role(name="A", owner_id=users[0].id)
    await make_user_role(users[1], role)

    await RoleRepository(db_session).delete_by_owner_ids([users[0].id])

    links = await db_session.scalar(
        select(func.count()).select_from(UserRole).where(UserRole.role_id == role.id)
    )
    assert links == 0


# BaseIdRepository.delete_by_id (проверяется на RoleRepository)
async def test_delete_by_id_found(db_session, role):
    """Deletes the row and returns True.

    Удаляет строку и возвращает True.
    """
    repo = RoleRepository(db_session)

    assert await repo.delete_by_id(role.id) is True
    assert await repo.get_by_id(role.id) is None


async def test_delete_by_id_unknown(db_session):
    """Unknown id -> False.

    Неизвестный id -> False.
    """
    assert await RoleRepository(db_session).delete_by_id(uuid4()) is False


async def test_delete_by_id_deletes_only_target(db_session, roles):
    """Only the target row is deleted.

    Удаляется только целевая строка.
    """
    repo = RoleRepository(db_session)

    await repo.delete_by_id(roles[0].id)

    assert await repo.get_by_id(roles[1].id) is not None
