# app/use_cases/system/organization/create_organization.py

"""
UseCase: создать организацию.
"""

import logging

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError
from app.dto import CurrentUser, OrganizationData, OrganizationOutPut
from app.repositories.protocols.system.organization import (
    OrganizationWriteRepositoryProtocol,
)
from app.repositories.protocols.system.user_organization import (
    UserOrganizationRepositoryProtocol,
)

logger = logging.getLogger(__name__)


async def create_organization(
    actor: CurrentUser,
    data: OrganizationData,
    *,
    organizations: OrganizationWriteRepositoryProtocol,
    user_organizations: UserOrganizationRepositoryProtocol,
) -> OrganizationOutPut:
    """
    Создать организацию для текущего пользователя.

    Связь с пользователем создаётся как связь владельца.
    """
    try:
        organization = await organizations.create_for_user(actor.id, data)
        await user_organizations.add_link(actor.id, organization.id)
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
        logger.exception("Unexpected IntegrityError in create_organization")
        raise ConflictError("Не удалось создать организацию.") from exc

    return organization
