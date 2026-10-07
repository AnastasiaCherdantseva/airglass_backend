from collections.abc import Awaitable, Callable
from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto import OrganizationData, OrganizationOutPut, OrganizationPatch
from app.models.system import Organization, User, UserOrganization
from app.repositories.system.organization import OrganizationRepository

MakeOrganization = Callable[..., Awaitable[Organization]]
MakeUserOrganization = Callable[[User, Organization], Awaitable[UserOrganization]]


async def _fetch_row(db_session: AsyncSession, organization_id: UUID):
    """
    Read (name, inn, address) straight from the DB, bypassing the identity map.

    Читает (name, inn, address) напрямую из БД, минуя identity map.
    """
    result = await db_session.execute(
        select(Organization.name, Organization.inn, Organization.address).where(
            Organization.id == organization_id
        )
    )
    return result.one_or_none()


async def _count_links(db_session: AsyncSession, organization_ids: list[UUID]) -> int:
    """
    Count user_organizations rows for the given organizations.

    Считает строки user_organizations для указанных организаций.
    """
    result = await db_session.scalar(
        select(func.count())
        .select_from(UserOrganization)
        .where(UserOrganization.organization_id.in_(organization_ids))
    )
    return result or 0


# ─────────────────────────────────────────────────────────────
# get_by_id
# ─────────────────────────────────────────────────────────────


async def test_get_by_id_success(db_session: AsyncSession, organization: Organization) -> None:
    """get_by_id находит существующую организацию."""
    repo = OrganizationRepository(db_session)

    found = await repo.get_by_id(organization.id)

    assert found is not None
    assert found.id == organization.id
    assert found.owner_id == organization.owner_id
    assert found.name == organization.name
    assert found.inn == organization.inn
    assert found.address == organization.address


async def test_get_by_id_not_found(db_session: AsyncSession) -> None:
    """get_by_id возвращает None для несуществующего id."""
    repo = OrganizationRepository(db_session)

    found = await repo.get_by_id(uuid4())

    assert found is None


# ─────────────────────────────────────────────────────────────
# get_by_user_id
# ─────────────────────────────────────────────────────────────


async def test_get_by_owner_id_includes_owned_organization(
    db_session: AsyncSession,
    user: User,
    organization: Organization,
) -> None:
    """Организация, где юзер владелец."""
    repo = OrganizationRepository(db_session)

    result = await repo.get_by_owner_id(user.id)

    assert len(result) == 1
    assert result[0].id == organization.id
    assert result[0].owner_id == user.id
    assert result[0].name == organization.name
    assert result[0].inn == organization.inn
    assert result[0].address == organization.address


async def test_get_by_owner_id_empty(db_session: AsyncSession, user: User) -> None:
    """Пустой список, если у юзера нет орг."""
    repo = OrganizationRepository(db_session)

    result = await repo.get_by_owner_id(user.id)

    assert result == []


async def test_get_by_owner_id_isolated(
    db_session: AsyncSession,
    users: list[User],
    make_organization: MakeOrganization,
) -> None:
    """Организации другого юзера не попадают."""
    user_a, user_b = users[0], users[1]
    org_a = await make_organization(owner=user_a)
    org_b = await make_organization(owner=user_b)
    repo = OrganizationRepository(db_session)

    result = await repo.get_by_owner_id(user_a.id)

    assert [o.id for o in result] == [org_a.id]


# ─────────────────────────────────────────────────────────────
# create_for_user
# ─────────────────────────────────────────────────────────────


async def test_create_for_user_returns_output(
    db_session: AsyncSession, user: User, new_organization_data: OrganizationData
) -> None:
    """create_for_user возвращает OrganizationOutPut с заполненными полями."""
    repo = OrganizationRepository(db_session)

    result = await repo.create_for_user(user.id, new_organization_data)

    assert isinstance(result, OrganizationOutPut)
    assert result.id is not None
    assert result.owner_id == user.id
    assert result.name == new_organization_data.name
    assert result.inn == new_organization_data.inn
    assert result.address == new_organization_data.address
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_create_for_user_persists_in_db(
    db_session: AsyncSession, user: User, new_organization_data: OrganizationData
) -> None:
    """После create_for_user организация реально в БД."""
    repo = OrganizationRepository(db_session)

    result = await repo.create_for_user(user.id, new_organization_data)

    row = await _fetch_row(db_session, result.id)
    assert row is not None
    assert tuple(row) == (
        new_organization_data.name,
        new_organization_data.inn,
        new_organization_data.address,
    )


async def test_create_for_user_address_none(
    db_session: AsyncSession, user: User, new_organization_data: OrganizationData
) -> None:
    """address=None допустим (поле опционально, BR-ORG-002)."""
    repo = OrganizationRepository(db_session)
    data = replace(new_organization_data, address=None)

    result = await repo.create_for_user(user.id, data)

    assert result.address is None


async def test_create_for_user_duplicate_inn_raises(
    db_session: AsyncSession,
    users: list[User],
    make_organization: MakeOrganization,
    new_organization_data: OrganizationData,
) -> None:
    """Дубликат inn (даже у другого владельца) → IntegrityError (BR-ORG-003)."""
    existing = await make_organization(owner=users[0])
    repo = OrganizationRepository(db_session)
    data = replace(new_organization_data, inn=existing.inn)

    with pytest.raises(IntegrityError):
        await repo.create_for_user(users[1].id, data)


async def test_create_for_user_duplicate_name_same_owner_raises(
    db_session: AsyncSession,
    user: User,
    organization: Organization,
    new_organization_data: OrganizationData,
) -> None:
    """Дубликат (owner_id, name) → IntegrityError (BR-ORG-004)."""
    repo = OrganizationRepository(db_session)
    data = replace(new_organization_data, name=organization.name)

    with pytest.raises(IntegrityError):
        await repo.create_for_user(user.id, data)


async def test_create_for_user_same_name_other_owner_ok(
    db_session: AsyncSession,
    users: list[User],
    make_organization: MakeOrganization,
    new_organization_data: OrganizationData,
) -> None:
    """Одинаковое name у разных владельцев допустимо (BR-ORG-004)."""
    existing = await make_organization(owner=users[0])
    repo = OrganizationRepository(db_session)
    data = replace(new_organization_data, name=existing.name)

    result = await repo.create_for_user(users[1].id, data)

    assert result.name == existing.name
    assert result.owner_id == users[1].id


# ─────────────────────────────────────────────────────────────
# patch
# ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("name", "Новое имя", id="name"),
        pytest.param("inn", "9999999999", id="inn"),
        pytest.param("address", "Новый адрес", id="address"),
    ],
)
async def test_patch_updates_single_field(
    db_session: AsyncSession,
    user: User,
    make_organization: MakeOrganization,
    field: str,
    value: str,
) -> None:
    """patch обновляет одно поле, остальные не меняются."""
    org = await make_organization(owner=user, address="Старый адрес")
    before = {"name": org.name, "inn": org.inn, "address": org.address}
    repo = OrganizationRepository(db_session)
    data = OrganizationPatch(id=org.id, **{field: value})

    result = await repo.patch(data)

    assert isinstance(result, OrganizationOutPut)
    assert getattr(result, field) == value
    for other in before.keys() - {field}:
        assert getattr(result, other) == before[other]


async def test_patch_updates_all_fields(
    db_session: AsyncSession, organization: Organization
) -> None:
    """patch обновляет name, inn и address одновременно."""
    repo = OrganizationRepository(db_session)
    data = OrganizationPatch(
        id=organization.id, name="Новое имя", inn="9999999999", address="Новый адрес"
    )

    result = await repo.patch(data)

    assert result is not None
    assert (result.name, result.inn, result.address) == ("Новое имя", "9999999999", "Новый адрес")
    assert result.owner_id == organization.owner_id


async def test_patch_persists_in_db(db_session: AsyncSession, organization: Organization) -> None:
    """Изменения patch реально в БД."""
    repo = OrganizationRepository(db_session)
    data = OrganizationPatch(
        id=organization.id, name="Новое имя", inn="9999999999", address="Новый адрес"
    )

    await repo.patch(data)

    row = await _fetch_row(db_session, organization.id)
    assert row is not None
    assert tuple(row) == ("Новое имя", "9999999999", "Новый адрес")


async def test_patch_not_found(db_session: AsyncSession) -> None:
    """patch возвращает None для несуществующей организации."""
    repo = OrganizationRepository(db_session)
    data = OrganizationPatch(id=uuid4(), name="Имя", inn=None, address=None)

    result = await repo.patch(data)

    assert result is None


async def test_patch_updates_updated_at(
    db_session: AsyncSession, user: User, make_organization: MakeOrganization
) -> None:
    """patch обновляет updated_at (TimestampMixin.onupdate)."""
    old = datetime(2020, 1, 1, tzinfo=UTC)
    org = await make_organization(owner=user, updated_at=old)
    repo = OrganizationRepository(db_session)
    data = OrganizationPatch(id=org.id, name="Новое имя", inn=None, address=None)

    result = await repo.patch(data)

    assert result is not None
    assert result.updated_at > old
    assert result.created_at == org.created_at


async def test_patch_duplicate_inn_raises(
    db_session: AsyncSession,
    users: list[User],
    make_organization: MakeOrganization,
) -> None:
    """Смена inn на уже занятый → IntegrityError (BR-ORG-003)."""
    taken = await make_organization(owner=users[0])
    target = await make_organization(owner=users[1])
    repo = OrganizationRepository(db_session)
    data = OrganizationPatch(id=target.id, name=None, inn=taken.inn, address=None)

    with pytest.raises(IntegrityError):
        await repo.patch(data)


# ─────────────────────────────────────────────────────────────
# delete_by_owner_ids
# ─────────────────────────────────────────────────────────────


async def test_delete_by_owner_ids_deletes_all_of_owners(
    db_session: AsyncSession,
    users: list[User],
    make_organization: MakeOrganization,
) -> None:
    """Удаляет все организации указанных владельцев, возвращает rowcount."""
    owner_a, owner_b = users[0], users[1]
    orgs = [
        await make_organization(owner=owner_a),
        await make_organization(owner=owner_a),
        await make_organization(owner=owner_b),
    ]
    repo = OrganizationRepository(db_session)

    rowcount = await repo.delete_by_owner_ids([owner_a.id, owner_b.id])

    assert rowcount == 3
    for org in orgs:
        assert await repo.get_by_id(org.id) is None


async def test_delete_by_owner_ids_empty_list(db_session: AsyncSession) -> None:
    """Пустой список → 0."""
    repo = OrganizationRepository(db_session)

    rowcount = await repo.delete_by_owner_ids([])

    assert rowcount == 0


async def test_delete_by_owner_ids_unknown_ids(
    db_session: AsyncSession, organization: Organization
) -> None:
    """Несуществующие owner_id → 0, существующие организации на месте."""
    repo = OrganizationRepository(db_session)

    rowcount = await repo.delete_by_owner_ids([uuid4(), uuid4()])

    assert rowcount == 0
    assert await repo.get_by_id(organization.id) is not None


async def test_delete_by_owner_ids_cascades_user_links(
    db_session: AsyncSession,
    users: list[User],
    make_organization: MakeOrganization,
    make_user_organization: MakeUserOrganization,
) -> None:
    """Связи user_organizations удаляются каскадом (BR-ORG-008)."""
    owner, member = users[0], users[1]
    org = await make_organization(owner=owner)
    await make_user_organization(owner, org)
    await make_user_organization(member, org)
    assert await _count_links(db_session, [org.id]) == 2
    repo = OrganizationRepository(db_session)

    await repo.delete_by_owner_ids([owner.id])

    assert await _count_links(db_session, [org.id]) == 0


async def test_delete_by_owner_ids_does_not_touch_other_owners(
    db_session: AsyncSession,
    users: list[User],
    make_organization: MakeOrganization,
    make_user_organization: MakeUserOrganization,
) -> None:
    """Организации и связи других владельцев не трогаются."""
    owner, other_owner = users[0], users[1]
    await make_organization(owner=owner)
    kept = await make_organization(owner=other_owner)
    await make_user_organization(other_owner, kept)
    repo = OrganizationRepository(db_session)

    rowcount = await repo.delete_by_owner_ids([owner.id])

    assert rowcount == 1
    assert await repo.get_by_id(kept.id) is not None
    assert await _count_links(db_session, [kept.id]) == 1
