from collections.abc import Callable
from uuid import uuid4

import pytest

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.dto import CurrentUser
from app.models.system import Organization, User
from app.use_cases.system.organization.delete_organization import delete_organization
from tests.unit.fakes.organization import FakeOrganizationRepository

MakeOrganization = Callable[..., Organization]


def _actor(user: User) -> CurrentUser:
    """Собрать CurrentUser из модели пользователя."""
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


async def _call(
    actor: User,
    organization_id,
    organizations: FakeOrganizationRepository,
) -> None:
    """Вызвать delete_organization от имени пользователя."""
    await delete_organization(
        _actor(actor),
        organization_id,
        organizations=organizations,
    )


# ─────────────────────────────────────────────────────────────
# 1, 5, 6. Успешное удаление
# ─────────────────────────────────────────────────────────────


async def test_delete_organization(
    users_in_memory: list[User],
    organization_in_memory: Organization,
) -> None:
    """Владелец может удалить свою организацию."""
    actor = users_in_memory[0]
    organizations = FakeOrganizationRepository([organization_in_memory])

    await _call(actor, organization_in_memory.id, organizations)

    result = await organizations.get_by_id(organization_in_memory.id)

    assert result is None


async def test_delete_does_not_affect_other_organizations(
    users_in_memory: list[User],
    organizations_in_memory: list[Organization],
) -> None:
    """Удаление одной организации не затрагивает остальные."""
    actor = users_in_memory[0]
    organization, other = organizations_in_memory[:2]
    organizations = FakeOrganizationRepository(organizations_in_memory)

    await _call(actor, organization.id, organizations)

    assert await organizations.get_by_id(organization.id) is None
    assert await organizations.get_by_id(other.id) is not None


async def test_delete_does_not_affect_other_owner_organizations(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
    organization_in_memory: Organization,
) -> None:
    """Удаление организации не затрагивает организацию другого владельца."""
    actor, other = users_in_memory[:2]
    other_organization = make_organization_in_memory(owner=other)
    organizations = FakeOrganizationRepository(
        [organization_in_memory, other_organization],
    )

    await _call(actor, organization_in_memory.id, organizations)

    assert await organizations.get_by_id(organization_in_memory.id) is None
    assert await organizations.get_by_id(other_organization.id) is not None


# ─────────────────────────────────────────────────────────────
# 3, 4, 7. Ошибки
# ─────────────────────────────────────────────────────────────


async def test_delete_not_found_raises_not_found(
    users_in_memory: list[User],
) -> None:
    """При отсутствии организации возникает NotFoundError."""
    actor = users_in_memory[0]
    organizations = FakeOrganizationRepository()

    with pytest.raises(NotFoundError, match="Организация не найдена"):
        await _call(actor, uuid4(), organizations)


async def test_delete_foreign_organization_raises_permission_denied(
    users_in_memory: list[User],
    make_organization_in_memory: MakeOrganization,
) -> None:
    """Нельзя удалить организацию другого пользователя."""
    actor, other = users_in_memory[:2]
    organization = make_organization_in_memory(owner=other)
    organizations = FakeOrganizationRepository([organization])

    with pytest.raises(
        PermissionDeniedError,
        match="принадлежит другому пользователю",
    ):
        await _call(actor, organization.id, organizations)

    assert await organizations.get_by_id(organization.id) is not None


async def test_delete_empty_repository_raises_not_found(
    users_in_memory: list[User],
) -> None:
    """Пустой репозиторий приводит к NotFoundError."""
    actor = users_in_memory[0]
    organization_id = uuid4()
    organizations = FakeOrganizationRepository()

    with pytest.raises(NotFoundError, match="Организация не найдена"):
        await _call(actor, organization_id, organizations)
