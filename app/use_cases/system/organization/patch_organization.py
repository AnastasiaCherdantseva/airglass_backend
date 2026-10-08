import logging

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.dto import CurrentUser, OrganizationOutPut, OrganizationPatch
from app.repositories.protocols.system.organization import (
    OrganizationRepositoryProtocol,
)

logger = logging.getLogger(__name__)


async def patch_organization(
    actor: CurrentUser,
    data: OrganizationPatch,
    *,
    organizations_repo: OrganizationRepositoryProtocol,
) -> OrganizationOutPut:
    """
    Изменить организацию, которой владеет текущий пользователь.
    """
    organization = await organizations_repo.get_by_id(data.id)
    if organization is None:
        logger.info("Organization patch failed: The organization (id: %s) not found", data.id)
        raise NotFoundError("Организация не найдена.")
    if organization.owner_id != actor.id:
        raise PermissionDeniedError("Организация принадлежит другому пользователю.")
    try:
        result = await organizations_repo.patch(data)
    except IntegrityError as exc:
        constraint_name = (
            getattr(exc.orig, "constraint_name", None)
            or getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
            or getattr(getattr(exc.orig, "__cause__", None), "constraint_name", "")
        )

        if constraint_name == "uq_organizations_inn":
            raise ConflictError("Организация с таким ИНН уже существует.") from exc

        if constraint_name == "uq_organizations_owner_name":
            raise ConflictError("У вас уже есть организация с таким названием.") from exc
        logger.exception("Unexpected IntegrityError in patch_organization")
        raise ConflictError("Не удалось обновить организацию.") from exc
    if result is None:
        logger.info("Organization patch failed: Organization %s disappeared", data.id)
        raise NotFoundError("Организация не найдена.")
    return result
