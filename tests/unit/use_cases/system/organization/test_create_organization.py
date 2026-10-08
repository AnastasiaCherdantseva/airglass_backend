"""Юнит-тесты use case create_organization (фейковые репозитории, без БД)."""

from collections.abc import Callable

import pytest

from app.core.exceptions import ConflictError
from app.dto import CurrentUser, OrganizationData, OrganizationOutPut
from app.models.system import Organization, User
from app.use_cases.system.organization.create_organization import (
    create_organization,
)
from tests.unit.fakes.organization import FakeOrganizationRepository
from tests.unit.fakes.user_organization_repository import (
    FakeUserOrganizationRepository,
)

MakeOrganization = Callable[..., Organization]
MakeOrganizationsRepo = Callable[..., FakeOrganizationRepository]
MakeUserOrganizationsRepo = Callable[
    ...,
    FakeUserOrganizationRepository,
]


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


def _data(
    *,
    name: str = "ООО Новая организация",
    inn: str = "7701234567",
    address: str | None = "г. Москва",
) -> OrganizationData:
    """Создаёт DTO для создания организации."""
    return OrganizationData(
        name=name,
        inn=inn,
        address=address,
    )


async def _call(
    actor: User,
    data: OrganizationData,
    organizations: FakeOrganizationRepository,
    user_organizations: FakeUserOrganizationRepository,
) -> OrganizationOutPut:
    """Вызывает create_organization от имени пользователя."""
    return await create_organization(
        _actor(actor),
        data,
        organizations=organizations,
        user_organizations=user_organizations,
    )


# ─────────────────────────────────────────────────────────────
# 1-5. Успешное создание
# ─────────────────────────────────────────────────────────────


async def test_create_organization_returns_all_output_fields(
    users_in_memory: list[User],
    make_organizations_repo: MakeOrganizationsRepo,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Успешное создание возвращает OrganizationOutPut со всеми полями."""
    actor = users_in_memory[0]
    organizations = make_organizations_repo()
    user_organizations = make_user_organizations_repo()
    data = _data()

    result = await _call(
        actor,
        data,
        organizations,
        user_organizations,
    )

    assert isinstance(result, OrganizationOutPut)
    assert result.id is not None
    assert result.owner_id == actor.id
    assert result.name == data.name
    assert result.inn == data.inn
    assert result.address == data.address
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_create_organization_uses_actor_as_owner(
    users_in_memory: list[User],
    make_organizations_repo: MakeOrganizationsRepo,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """owner_id организации берётся из actor, а не из DTO."""
    actor = users_in_memory[0]
    organizations = make_organizations_repo()
    user_organizations = make_user_organizations_repo()
    data = _data()

    result = await _call(
        actor,
        data,
        organizations,
        user_organizations,
    )

    assert not hasattr(data, "owner_id")
    assert result.owner_id == actor.id


async def test_create_organization_creates_owner_link(
    users_in_memory: list[User],
    make_organizations_repo: MakeOrganizationsRepo,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """После создания появляется связь actor ↔ organization."""
    actor = users_in_memory[0]
    organizations = make_organizations_repo()
    user_organizations = make_user_organizations_repo()

    result = await _call(
        actor,
        _data(),
        organizations,
        user_organizations,
    )

    assert (actor.id, result.id) in user_organizations.links


async def test_create_organization_is_stored_in_fake(
    users_in_memory: list[User],
    make_organizations_repo: MakeOrganizationsRepo,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Созданная организация действительно сохраняется в fake."""
    actor = users_in_memory[0]
    organizations = make_organizations_repo()
    user_organizations = make_user_organizations_repo()

    result = await _call(
        actor,
        _data(),
        organizations,
        user_organizations,
    )

    stored = await organizations.get_by_id(result.id)

    assert stored is not None
    assert stored.id == result.id
    assert stored.owner_id == actor.id
    assert stored.name == result.name
    assert stored.inn == result.inn
    assert stored.address == result.address


async def test_create_organization_with_none_address(
    users_in_memory: list[User],
    make_organizations_repo: MakeOrganizationsRepo,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """address=None корректно сохраняется."""
    actor = users_in_memory[0]
    organizations = make_organizations_repo()
    user_organizations = make_user_organizations_repo()

    result = await _call(
        actor,
        _data(address=None),
        organizations,
        user_organizations,
    )

    assert result.address is None


# ─────────────────────────────────────────────────────────────
# 6-8. Конфликты
# ─────────────────────────────────────────────────────────────


async def test_duplicate_inn_raises_conflict(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    make_organizations_repo: MakeOrganizationsRepo,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Дубликат ИНН приводит к ConflictError с сообщением про ИНН."""
    actor = users_in_memory[0]
    existing = make_organization_in_memory(
        owner=actor,
        inn="7701234567",
    )
    organizations = make_organizations_repo(existing)
    user_organizations = make_user_organizations_repo(existing)

    with pytest.raises(ConflictError, match="ИНН"):
        await _call(
            actor,
            _data(inn=existing.inn, name="Другая организация"),
            organizations,
            user_organizations,
        )

    assert user_organizations.links == {}


async def test_duplicate_owner_name_raises_conflict(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    make_organizations_repo: MakeOrganizationsRepo,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Дубликат имени у одного владельца приводит к ConflictError."""
    actor = users_in_memory[0]
    existing = make_organization_in_memory(
        owner=actor,
        name="ООО Ромашка",
        inn="7701234567",
    )
    organizations = make_organizations_repo(existing)
    user_organizations = make_user_organizations_repo(existing)

    with pytest.raises(ConflictError, match="названием"):
        await _call(
            actor,
            _data(
                name=existing.name,
                inn="7707654321",
            ),
            organizations,
            user_organizations,
        )

    assert user_organizations.links == {}


async def test_no_owner_link_is_created_when_create_fails(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    make_organizations_repo: MakeOrganizationsRepo,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """При ошибке create_for_user add_link не вызывается."""
    actor = users_in_memory[0]
    existing = make_organization_in_memory(
        owner=actor,
        inn="7701234567",
    )
    organizations = make_organizations_repo(existing)
    user_organizations = make_user_organizations_repo()

    with pytest.raises(ConflictError):
        await _call(
            actor,
            _data(inn=existing.inn),
            organizations,
            user_organizations,
        )

    assert user_organizations.links == {}


# ─────────────────────────────────────────────────────────────
# 9. Разные владельцы
# ─────────────────────────────────────────────────────────────


async def test_same_name_is_allowed_for_different_owner(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    make_organizations_repo: MakeOrganizationsRepo,
    make_user_organizations_repo: MakeUserOrganizationsRepo,
) -> None:
    """Одинаковое имя разрешено для организаций разных владельцев."""
    actor, other = users_in_memory[:2]

    existing = make_organization_in_memory(
        owner=other,
        name="ООО Ромашка",
        inn="7701234567",
    )
    organizations = make_organizations_repo(existing)
    user_organizations = make_user_organizations_repo(existing)

    result = await _call(
        actor,
        _data(
            name=existing.name,
            inn="7707654321",
        ),
        organizations,
        user_organizations,
    )

    assert result.name == existing.name
    assert result.owner_id == actor.id
    assert result.inn != existing.inn
    assert (actor.id, result.id) in user_organizations.links
