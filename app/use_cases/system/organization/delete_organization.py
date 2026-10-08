import logging
from uuid import UUID

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.dto import CurrentUser
from app.repositories.protocols.system.organization import (
    OrganizationRepositoryProtocol,
)

logger = logging.getLogger(__name__)


async def delete_organization(
    actor: CurrentUser,
    organization_id: UUID,
    *,
    organizations: OrganizationRepositoryProtocol,
) -> None:
    """
    Удалить организацию, которой владеет текущий пользователь.
    """
    organization = await organizations.get_by_id(organization_id)

    if organization is None:
        logger.info(
            "Organization deletion failed: The organization (id: %s) not found",
            organization_id,
        )
        raise NotFoundError("Организация не найдена.")

    if organization.owner_id != actor.id:
        logger.info(
            "Organization deletion denied: The organization (id: %s) belongs to another user",
            organization_id,
        )
        raise PermissionDeniedError("Организация принадлежит другому пользователю.")

    deleted = await organizations.delete_by_id(organization_id)

    if not deleted:
        logger.info(
            "Organization deletion failed: Organization %s disappeared",
            organization_id,
        )
        raise NotFoundError("Организация не найдена.")
