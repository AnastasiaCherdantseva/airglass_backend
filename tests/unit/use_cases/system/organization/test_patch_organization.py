"""Юнит-тесты use case patch_organization (фейковые репозитории, без БД)."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.dto import CurrentUser, OrganizationOutPut, OrganizationPatch
from app.models.system import Organization, User
from app.use_cases.system.organization.patch_organization import patch_organization
from tests.unit.fakes.organization import FakeOrganizationRepository

MakeOrganization = Callable[..., Organization]
MakeOrganizationsRepo = Callable[..., FakeOrganizationRepository]


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


def _patch(
    organization: Organization,
    *,
    name: str | None = None,
    inn: str | None = None,
    address: str | None = None,
) -> OrganizationPatch:
    """Создаёт DTO для частичного обновления."""
    return OrganizationPatch(
        id=organization.id,
        name=name,
        inn=inn,
        address=address,
    )


async def _call(
    actor: User,
    data: OrganizationPatch,
    organizations: FakeOrganizationRepository,
) -> OrganizationOutPut:
    """Вызывает patch_organization от имени пользователя."""
    return await patch_organization(
        _actor(actor),
        data,
        organizations_repo=organizations,
    )


# ─────────────────────────────────────────────────────────────
# 1-8. Успешное обновление
# ─────────────────────────────────────────────────────────────


async def test_patch_name_updates_only_name(
    users_in_memory: list[User],
    organization_in_memory: Organization,
) -> None:
    """Обновление name не меняет остальные поля."""
    actor = users_in_memory[0]
    old = organization_in_memory
    organizations = FakeOrganizationRepository([old])

    result = await _call(
        actor,
        _patch(old, name="Новое название"),
        organizations,
    )

    assert result.name == "Новое название"
    assert result.inn == old.inn
    assert result.address == old.address
    assert result.owner_id == old.owner_id


async def test_patch_inn_updates_only_inn(
    users_in_memory: list[User],
    organization_in_memory: Organization,
) -> None:
    """Обновление inn не меняет остальные поля."""
    actor = users_in_memory[0]
    old = organization_in_memory
    organizations = FakeOrganizationRepository([old])

    result = await _call(
        actor,
        _patch(old, inn="7709876543"),
        organizations,
    )

    assert result.name == old.name
    assert result.inn == "7709876543"
    assert result.address == old.address
    assert result.owner_id == old.owner_id


async def test_patch_address_updates_only_address(
    users_in_memory: list[User],
    organization_in_memory: Organization,
) -> None:
    """Обновление address не меняет остальные поля."""
    actor = users_in_memory[0]
    old = organization_in_memory
    organizations = FakeOrganizationRepository([old])

    result = await _call(
        actor,
        _patch(old, address="г. Москва, ул. Новая, 10"),
        organizations,
    )

    assert result.name == old.name
    assert result.inn == old.inn
    assert result.address == "г. Москва, ул. Новая, 10"
    assert result.owner_id == old.owner_id


async def test_patch_all_fields(
    users_in_memory: list[User],
    organization_in_memory: Organization,
) -> None:
    """Одновременное обновление name, inn и address меняет все три поля."""
    actor = users_in_memory[0]
    old = organization_in_memory
    organizations = FakeOrganizationRepository([old])

    result = await _call(
        actor,
        _patch(
            old,
            name="ООО Новая",
            inn="7709876543",
            address="г. Санкт-Петербург",
        ),
        organizations,
    )

    assert result.name == "ООО Новая"
    assert result.inn == "7709876543"
    assert result.address == "г. Санкт-Петербург"
    assert result.owner_id == old.owner_id


async def test_patch_address_none(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
) -> None:
    """address=None допускается и возвращается в DTO."""
    actor = users_in_memory[0]
    organization = make_organization_in_memory(
        owner=actor,
        address=None,
    )
    organizations = FakeOrganizationRepository([organization])

    result = await _call(
        actor,
        _patch(organization, address=None),
        organizations,
    )

    assert result.address is None


async def test_patch_changes_organization_in_fake(
    users_in_memory: list[User],
    organization_in_memory: Organization,
) -> None:
    """После patch обновлённые значения доступны через get_by_id."""
    actor = users_in_memory[0]
    organizations = FakeOrganizationRepository([organization_in_memory])

    await _call(
        actor,
        _patch(
            organization_in_memory,
            name="Новое название",
            inn="7709876543",
            address="г. Казань",
        ),
        organizations,
    )

    stored = await organizations.get_by_id(organization_in_memory.id)

    assert stored is not None
    assert stored.name == "Новое название"
    assert stored.inn == "7709876543"
    assert stored.address == "г. Казань"


async def test_patch_does_not_change_owner_id(
    users_in_memory: list[User],
    organization_in_memory: Organization,
) -> None:
    """Patch не меняет owner_id организации."""
    actor = users_in_memory[0]
    organizations = FakeOrganizationRepository([organization_in_memory])
    old_owner_id = organization_in_memory.owner_id

    result = await _call(
        actor,
        _patch(
            organization_in_memory,
            name="Новое название",
            inn="7709876543",
        ),
        organizations,
    )

    assert result.owner_id == old_owner_id
    assert result.owner_id == actor.id


async def test_patch_updates_updated_at(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
) -> None:
    """После изменения updated_at становится новее старого значения."""
    actor = users_in_memory[0]
    old_updated_at = datetime.now(UTC) - timedelta(hours=1)

    organization = make_organization_in_memory(
        owner=actor,
        updated_at=old_updated_at,
    )
    organizations = FakeOrganizationRepository([organization])

    result = await _call(
        actor,
        _patch(organization, name="Новое название"),
        organizations,
    )

    assert result.updated_at > old_updated_at


# ─────────────────────────────────────────────────────────────
# 9-10. Проверки доступа
# ─────────────────────────────────────────────────────────────


async def test_patch_not_found_raises_not_found(
    users_in_memory: list[User],
) -> None:
    """Если организации нет, возникает NotFoundError."""
    actor = users_in_memory[0]
    organizations = FakeOrganizationRepository()
    organization_id = uuid4()

    with pytest.raises(NotFoundError, match="Организация не найдена"):
        await _call(
            actor,
            OrganizationPatch(id=organization_id, name="Новое название"),
            organizations,
        )


async def test_patch_foreign_organization_raises_permission_denied(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
) -> None:
    """Нельзя изменить организацию другого пользователя."""
    actor, other = users_in_memory[:2]
    organization = make_organization_in_memory(owner=other)
    organizations = FakeOrganizationRepository([organization])

    with pytest.raises(
        PermissionDeniedError,
        match="принадлежит другому пользователю",
    ):
        await _call(
            actor,
            _patch(organization, name="Новое название"),
            organizations,
        )

    stored = await organizations.get_by_id(organization.id)

    assert stored is not None
    assert stored.name == organization.name


# ─────────────────────────────────────────────────────────────
# 11-13. Конфликты
# ─────────────────────────────────────────────────────────────


async def test_patch_duplicate_inn_raises_conflict(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    make_organizations_repo: MakeOrganizationsRepo,
) -> None:
    """Дубликат ИНН приводит к ConflictError."""
    actor = users_in_memory[0]
    organization = make_organization_in_memory(
        owner=actor,
        inn="7701234567",
    )
    duplicate = make_organization_in_memory(
        owner=actor,
        inn="7707654321",
    )
    organizations = make_organizations_repo(organization, duplicate)

    with pytest.raises(ConflictError, match="ИНН"):
        await _call(
            actor,
            _patch(duplicate, inn=organization.inn),
            organizations,
        )


async def test_patch_duplicate_owner_name_raises_conflict(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    make_organizations_repo: MakeOrganizationsRepo,
) -> None:
    """Дубликат имени у одного владельца приводит к ConflictError."""
    actor = users_in_memory[0]
    organization = make_organization_in_memory(
        owner=actor,
        name="ООО Ромашка",
        inn="7701234567",
    )
    duplicate = make_organization_in_memory(
        owner=actor,
        name="ООО Другая",
        inn="7707654321",
    )
    organizations = make_organizations_repo(organization, duplicate)

    with pytest.raises(ConflictError, match="названием"):
        await _call(
            actor,
            _patch(duplicate, name=organization.name),
            organizations,
        )


async def test_patch_conflict_does_not_change_organization(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    make_organizations_repo: MakeOrganizationsRepo,
) -> None:
    """При ConflictError исходные значения организации не меняются."""
    actor = users_in_memory[0]
    organization = make_organization_in_memory(
        owner=actor,
        inn="7701234567",
        name="ООО Ромашка",
    )
    duplicate = make_organization_in_memory(
        owner=actor,
        inn="7707654321",
        name="ООО Другая",
    )
    organizations = make_organizations_repo(organization, duplicate)

    old_name = duplicate.name
    old_inn = duplicate.inn
    old_address = duplicate.address
    old_updated_at = duplicate.updated_at

    with pytest.raises(ConflictError):
        await _call(
            actor,
            _patch(
                duplicate,
                name=organization.name,
                inn=organization.inn,
            ),
            organizations,
        )

    stored = await organizations.get_by_id(duplicate.id)

    assert stored is not None
    assert stored.name == old_name
    assert stored.inn == old_inn
    assert stored.address == old_address
    assert stored.updated_at == old_updated_at


async def test_patch_same_name_and_inn_does_not_raise(
    users_in_memory: list[User],
    organization_in_memory: Organization,
    fake_organizations_repo: FakeOrganizationRepository,
) -> None:
    """Проверить обновление с теми же name и inn."""
    actor = users_in_memory[0]
    data = OrganizationPatch(
        id=organization_in_memory.id,
        name=organization_in_memory.name,
        inn=organization_in_memory.inn,
    )
    fake_organizations_repo.add(organization_in_memory)
    result = await _call(
        actor,
        data,
        fake_organizations_repo,
    )

    assert result.name == organization_in_memory.name
    assert result.inn == organization_in_memory.inn
