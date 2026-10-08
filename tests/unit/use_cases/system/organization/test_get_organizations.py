"""Юнит-тесты use case get_organizations (фейковые репозитории, без БД)."""

from collections.abc import Callable
from uuid import uuid4

from app.dto import CurrentUser, OrganizationOutPut
from app.models.system import Organization, User
from app.use_cases.system.organization.get_organizations import get_organizations
from tests.unit.fakes.user_organization_repository import FakeUserOrganizationRepository

MakeOrganization = Callable[..., Organization]
MakeUserOrganizationsRepo = Callable[..., FakeUserOrganizationRepository]


def _actor(user: User) -> CurrentUser:
    """Собирает CurrentUser из модели пользователя."""
    return CurrentUser(
        id=user.id,
        email=user.email,
        name=user.name,
        is_active=True,
        parent_id=None,
        children_count=0,
        permissions=[],
        has_admin_access=False,
    )


async def _call(user: User, repo: FakeUserOrganizationRepository) -> list[OrganizationOutPut]:
    """Вызывает get_organizations от имени user."""
    return await get_organizations(_actor(user), user_organizations=repo)


async def _link(repo: FakeUserOrganizationRepository, user: User, *orgs: Organization) -> None:
    """Привязывает организации к пользователю в фейковом репозитории."""
    for org in orgs:
        await repo.add_link(user.id, org.id)


# ─────────────────────────────────────────────────────────────
# 1, 6. Пусто
# ─────────────────────────────────────────────────────────────


async def test_empty_repository_returns_empty() -> None:
    """Полностью пустой репозиторий (нет юзеров, орг и связей) -> [] без ошибки."""
    repo = FakeUserOrganizationRepository()

    result = await _call(User(id=uuid4(), name="Аноним", email="a@example.com"), repo)

    assert result == []


# ─────────────────────────────────────────────────────────────
# 2-3. Одна и несколько
# ─────────────────────────────────────────────────────────────


async def test_one_organization(
    users_in_memory: list[User],
    organization_in_memory: Organization,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Одна связь -> одна организация."""
    actor = users_in_memory[0]
    repo = make_user_organizations_repo(organization_in_memory)
    await _link(repo, actor, organization_in_memory)

    result = await _call(actor, repo)

    assert [o.id for o in result] == [organization_in_memory.id]


async def test_several_organizations(
    users_in_memory: list[User],
    organizations_in_memory: list[Organization],
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Три связи -> три организации (порядок не гарантируется)."""
    actor = users_in_memory[0]
    repo = make_user_organizations_repo(*organizations_in_memory)
    await _link(repo, actor, *organizations_in_memory)

    result = await _call(actor, repo)

    assert len(result) == 3
    assert {o.id for o in result} == {o.id for o in organizations_in_memory}


# ─────────────────────────────────────────────────────────────
# 4. Изоляция
# ─────────────────────────────────────────────────────────────


async def test_other_users_organizations_are_isolated(
    users_in_memory: list[User],
    organizations_in_memory: list[Organization],
    make_organization_in_memory: MakeOrganization,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Организации другого юзера не попадают в результат актора."""
    actor, other = users_in_memory[0], users_in_memory[1]
    foreign = [make_organization_in_memory(owner=other) for _ in range(2)]
    repo = make_user_organizations_repo(*organizations_in_memory, *foreign)
    await _link(repo, actor, *organizations_in_memory)
    await _link(repo, other, *foreign)

    result = await _call(actor, repo)

    ids = {o.id for o in result}
    assert ids == {o.id for o in organizations_in_memory}
    assert ids.isdisjoint({o.id for o in foreign})


async def test_member_of_foreign_organization_is_returned(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Выборка идёт по связи, а не по владению: чужая организация, где актор участник, возвращается."""
    actor, other = users_in_memory[0], users_in_memory[1]
    foreign = make_organization_in_memory(owner=other)
    repo = make_user_organizations_repo(foreign)
    await _link(repo, actor, foreign)

    result = await _call(actor, repo)

    assert [(o.id, o.owner_id) for o in result] == [(foreign.id, other.id)]


# ─────────────────────────────────────────────────────────────
# 5. Поля DTO
# ─────────────────────────────────────────────────────────────


async def test_output_fields_are_filled(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Все поля OrganizationOutPut заполнены значениями из модели."""
    actor = users_in_memory[0]
    org = make_organization_in_memory(owner=actor, address="г. Москва")
    repo = make_user_organizations_repo(org)
    await _link(repo, actor, org)

    result = await _call(actor, repo)

    assert len(result) == 1
    out = result[0]
    assert out.id == org.id
    assert out.owner_id == actor.id
    assert out.name == org.name
    assert out.inn == org.inn
    assert out.address == "г. Москва"
    assert out.created_at == org.created_at
    assert out.updated_at == org.updated_at


async def test_address_none_is_kept(
    users_in_memory: list[User],
    organization_in_memory: Organization,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """address=None (поле опционально, BR-ORG-002) не ломает DTO."""
    actor = users_in_memory[0]
    repo = make_user_organizations_repo(organization_in_memory)
    await _link(repo, actor, organization_in_memory)

    result = await _call(actor, repo)

    assert result[0].address is None
