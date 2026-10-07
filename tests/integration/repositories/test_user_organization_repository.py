from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import Organization, User, UserOrganization
from app.repositories.system.organization import OrganizationRepository
from app.repositories.system.user import UserRepository
from app.repositories.system.user_organization import UserOrganizationRepository

MakeUserOrganization = Callable[[User, Organization], Awaitable[UserOrganization]]


async def _link_exists(db_session: AsyncSession, user_id: UUID, organization_id: UUID) -> bool:
    """
    Check the link directly in the DB, bypassing the identity map.

    Проверяет связь напрямую в БД, минуя identity map.
    """
    count = await db_session.scalar(
        select(func.count())
        .select_from(UserOrganization)
        .where(
            UserOrganization.user_id == user_id,
            UserOrganization.organization_id == organization_id,
        )
    )
    return bool(count)


# ─────────────────────────────────────────────────────────────
# add_link
# ─────────────────────────────────────────────────────────────


async def test_add_link(db_session: AsyncSession, user: User, organization: Organization) -> None:
    """add_link создаёт связь user <-> organization."""
    repo = UserOrganizationRepository(db_session)

    await repo.add_link(user.id, organization.id)

    assert await _link_exists(db_session, user.id, organization.id) is True


async def test_add_link_duplicate_raises(
    db_session: AsyncSession, user: User, organization: Organization
) -> None:
    """Повторный add_link для той же пары → IntegrityError."""
    repo = UserOrganizationRepository(db_session)
    await repo.add_link(user.id, organization.id)

    with pytest.raises(IntegrityError):
        await repo.add_link(user.id, organization.id)


async def test_add_link_does_not_create_extra_links(
    db_session: AsyncSession, users: list[User], organization: Organization
) -> None:
    """add_link создаёт ровно одну связь для указанной пары."""
    repo = UserOrganizationRepository(db_session)

    await repo.add_link(users[0].id, organization.id)

    assert await _link_exists(db_session, users[1].id, organization.id) is False


# ─────────────────────────────────────────────────────────────
# remove_link
# ─────────────────────────────────────────────────────────────


async def test_remove_link_found(
    db_session: AsyncSession,
    user: User,
    organization: Organization,
    make_user_organization: MakeUserOrganization,
) -> None:
    """remove_link удаляет связь, возвращает True."""
    await make_user_organization(user, organization)
    repo = UserOrganizationRepository(db_session)

    result = await repo.remove_link(user.id, organization.id)

    assert result is True
    assert await _link_exists(db_session, user.id, organization.id) is False


async def test_remove_link_not_found(
    db_session: AsyncSession, user: User, organization: Organization
) -> None:
    """remove_link возвращает False, если связи не было."""
    repo = UserOrganizationRepository(db_session)

    result = await repo.remove_link(user.id, organization.id)

    assert result is False


async def test_remove_link_does_not_touch_other_links(
    db_session: AsyncSession,
    users: list[User],
    organization: Organization,
    make_user_organization: MakeUserOrganization,
) -> None:
    """remove_link удаляет только указанную связь."""
    await make_user_organization(users[0], organization)
    await make_user_organization(users[1], organization)
    repo = UserOrganizationRepository(db_session)

    await repo.remove_link(users[0].id, organization.id)

    assert await _link_exists(db_session, users[1].id, organization.id) is True


# ─────────────────────────────────────────────────────────────
# remove_by_user_id
# ─────────────────────────────────────────────────────────────


async def test_remove_by_user_id(
    db_session: AsyncSession,
    user: User,
    organizations: list[Organization],
    make_user_organization: MakeUserOrganization,
) -> None:
    """Удаляет все связи юзера, возвращает rowcount."""
    for org in organizations:
        await make_user_organization(user, org)
    repo = UserOrganizationRepository(db_session)

    rowcount = await repo.remove_by_user_id(user.id)

    assert rowcount == 3
    assert await repo.get_organization_ids_by_user_id(user.id) == []


async def test_remove_by_user_id_does_not_touch_other_users(
    db_session: AsyncSession,
    users: list[User],
    organizations: list[Organization],
    make_user_organization: MakeUserOrganization,
) -> None:
    """Связи других юзеров не трогаются."""
    user_a, user_b = users[0], users[1]
    for org in organizations:
        await make_user_organization(user_a, org)
        await make_user_organization(user_b, org)
    repo = UserOrganizationRepository(db_session)

    await repo.remove_by_user_id(user_a.id)

    assert set(await repo.get_organization_ids_by_user_id(user_b.id)) == {
        o.id for o in organizations
    }


async def test_remove_by_user_id_unknown(db_session: AsyncSession) -> None:
    """Несуществующий юзер → 0."""
    repo = UserOrganizationRepository(db_session)

    rowcount = await repo.remove_by_user_id(uuid4())

    assert rowcount == 0


async def test_remove_by_user_id_keeps_organizations(
    db_session: AsyncSession,
    user: User,
    organizations: list[Organization],
    make_user_organization: MakeUserOrganization,
) -> None:
    """Организации не удаляются при разрыве связи."""
    for org in organizations:
        await make_user_organization(user, org)
    repo = UserOrganizationRepository(db_session)

    await repo.remove_by_user_id(user.id)

    # организации на месте
    org_repo = OrganizationRepository(db_session)
    for org in organizations:
        assert await org_repo.get_by_id(org.id) is not None


# ─────────────────────────────────────────────────────────────
# remove_by_organization_id
# ─────────────────────────────────────────────────────────────


async def test_remove_by_organization_id(
    db_session: AsyncSession,
    users: list[User],
    organization: Organization,
    make_user_organization: MakeUserOrganization,
) -> None:
    """Удаляет все связи организации, возвращает rowcount."""
    for u in users[:3]:
        await make_user_organization(u, organization)
    repo = UserOrganizationRepository(db_session)

    rowcount = await repo.remove_by_organization_id(organization.id)

    assert rowcount == 3
    assert await repo.get_user_ids_by_organization_id(organization.id) == []


async def test_remove_by_organization_id_does_not_touch_other_orgs(
    db_session: AsyncSession,
    user: User,
    organizations: list[Organization],
    make_user_organization: MakeUserOrganization,
) -> None:
    """Связи других организаций не трогаются."""
    org_a, org_b = organizations[0], organizations[1]
    await make_user_organization(user, org_a)
    await make_user_organization(user, org_b)
    repo = UserOrganizationRepository(db_session)

    await repo.remove_by_organization_id(org_a.id)

    assert await repo.get_organization_ids_by_user_id(user.id) == [org_b.id]


async def test_remove_by_organization_id_unknown(db_session: AsyncSession) -> None:
    """Несуществующая организация → 0."""
    repo = UserOrganizationRepository(db_session)

    rowcount = await repo.remove_by_organization_id(uuid4())

    assert rowcount == 0


async def test_remove_by_organization_id_keeps_users(
    db_session: AsyncSession,
    users: list[User],
    organization: Organization,
    make_user_organization: MakeUserOrganization,
) -> None:
    """Юзеры не удаляются при разрыве связи."""
    for u in users[:3]:
        await make_user_organization(u, organization)
    repo = UserOrganizationRepository(db_session)

    await repo.remove_by_organization_id(organization.id)

    user_repo = UserRepository(db_session)
    for u in users[:3]:
        assert await user_repo.get_by_id(u.id) is not None


# ─────────────────────────────────────────────────────────────
# get_user_ids_by_organization_id
# ─────────────────────────────────────────────────────────────


async def test_get_user_ids_by_organization_id(
    db_session: AsyncSession,
    users: list[User],
    organization: Organization,
    make_user_organization: MakeUserOrganization,
) -> None:
    """Возвращает user_id всех участников организации."""
    await make_user_organization(users[0], organization)
    await make_user_organization(users[1], organization)
    repo = UserOrganizationRepository(db_session)

    result = await repo.get_user_ids_by_organization_id(organization.id)

    assert set(result) == {users[0].id, users[1].id}


async def test_get_user_ids_by_organization_id_empty(
    db_session: AsyncSession, organization: Organization
) -> None:
    """Пустой список, если в организации никого нет."""
    repo = UserOrganizationRepository(db_session)

    result = await repo.get_user_ids_by_organization_id(organization.id)

    assert result == []


async def test_get_user_ids_by_organization_id_isolated(
    db_session: AsyncSession,
    users: list[User],
    organizations: list[Organization],
    make_user_organization: MakeUserOrganization,
) -> None:
    """Участники другой организации не попадают."""
    org_a, org_b = organizations[0], organizations[1]
    await make_user_organization(users[0], org_a)
    await make_user_organization(users[1], org_b)
    repo = UserOrganizationRepository(db_session)

    result = await repo.get_user_ids_by_organization_id(org_a.id)

    assert result == [users[0].id]


# ─────────────────────────────────────────────────────────────
# get_organization_ids_by_user_id
# ─────────────────────────────────────────────────────────────


async def test_get_organization_ids_by_user_id(
    db_session: AsyncSession,
    user: User,
    organizations: list[Organization],
    make_user_organization: MakeUserOrganization,
) -> None:
    """Возвращает organization_id всех организаций юзера."""
    for org in organizations:
        await make_user_organization(user, org)
    repo = UserOrganizationRepository(db_session)

    result = await repo.get_organization_ids_by_user_id(user.id)

    assert set(result) == {o.id for o in organizations}


async def test_get_organization_ids_by_user_id_empty(db_session: AsyncSession, user: User) -> None:
    """Пустой список, если юзер нигде не состоит."""
    repo = UserOrganizationRepository(db_session)

    result = await repo.get_organization_ids_by_user_id(user.id)

    assert result == []


async def test_get_organization_ids_by_user_id_isolated(
    db_session: AsyncSession,
    users: list[User],
    organizations: list[Organization],
    make_user_organization: MakeUserOrganization,
) -> None:
    """Организации другого юзера не попадают."""
    await make_user_organization(users[0], organizations[0])
    await make_user_organization(users[1], organizations[1])
    repo = UserOrganizationRepository(db_session)

    result = await repo.get_organization_ids_by_user_id(users[0].id)

    assert result == [organizations[0].id]
