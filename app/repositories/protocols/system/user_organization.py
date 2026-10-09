from typing import Protocol
from uuid import UUID

from app.dto.system.organization import OrganizationOutPut


class UserOrganizationReadRepositoryProtocol(Protocol):
    """Контракт чтения связей пользователей и организаций."""

    async def get_user_ids_by_organization_id(
        self,
        organization_id: UUID,
    ) -> list[UUID]: ...

    async def get_organization_ids_by_user_id(
        self,
        user_id: UUID,
    ) -> list[UUID]: ...
    async def get_organizations_by_user_id(
        self,
        user_id: UUID,
    ) -> list[OrganizationOutPut]: ...


class UserOrganizationWriteRepositoryProtocol(Protocol):
    """Контракт записи связей пользователей и организаций."""

    async def add_link(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> None: ...
    async def add_links_to_user(
        self,
        user_id: UUID,
        organization_ids: list[UUID],
    ) -> None: ...

    async def remove_link(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> bool: ...

    async def remove_by_user_id(
        self,
        user_id: UUID,
    ) -> int: ...

    async def remove_by_organization_id(
        self,
        organization_id: UUID,
    ) -> int: ...


class UserOrganizationRepositoryProtocol(
    UserOrganizationReadRepositoryProtocol,
    UserOrganizationWriteRepositoryProtocol,
    Protocol,
):
    """Полный контракт репозитория связей пользователей и организаций."""

    pass
