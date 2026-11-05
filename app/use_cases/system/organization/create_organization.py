# app/use_cases/system/organization/create_organization.py

"""
UseCase: создать организацию.
"""

import logging
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError
from app.dto import CurrentUser, OrganizationData, OrganizationOutPut
from app.dto.system.permission_condition import PermissionConditionAllData
from app.models.system.permission_condition import ConditionType
from app.repositories.protocols.system.organization import (
    OrganizationWriteRepositoryProtocol,
)
from app.repositories.protocols.system.permission_condition import PermissionConditionWriteRepositoryProtocol
from app.repositories.protocols.system.user_direct_permission import UserDirectPermissionWriteRepositoryProtocol
from app.repositories.protocols.system.user_organization import (
    UserOrganizationRepositoryProtocol,
)
from app.repositories.protocols.system.user_permission import UserPermissionWriteRepositoryProtocol
from app.services.grant_conditions import grant_conditions_to_user

logger = logging.getLogger(__name__)

NEW_ORGS_CONDITION_CODES: dict[str, ConditionType] = {
    "ORGANIZATIONS.READ": ConditionType.ORGANIZATION,
}


async def create_organization(
    actor: CurrentUser,
    data: OrganizationData,
    *,
    organizations: OrganizationWriteRepositoryProtocol,
    user_organizations: UserOrganizationRepositoryProtocol,
    permission_conditions: PermissionConditionWriteRepositoryProtocol,
    user_direct_permissions: UserDirectPermissionWriteRepositoryProtocol,
    user_permissions: UserPermissionWriteRepositoryProtocol,
) -> OrganizationOutPut:
    """
    Создать организацию и права для нее для текущего пользователя.
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

    new_conditions: list[UUID] = []
    for code, cond_type in NEW_ORGS_CONDITION_CODES.items():
            permission = next((p for p in actor.permissions if p.code == code), None)
            if permission is None:
                logger.warning(
                    "Create organization warning: permission %s not found (actor=%s, organization=%s) — skipped",
                    code,
                    actor.id,
                    organization.id,
                )
                continue
            new_data = PermissionConditionAllData(
                permission_id=permission.id,
                type=cond_type,
                organization_id=organization.id,
                is_active=True,
            )
            new_cond = await permission_conditions.create(new_data)
            new_conditions.append(new_cond.id)

    await grant_conditions_to_user(
            actor.id,
            new_conditions,
            user_direct_permissions=user_direct_permissions,
            user_permissions=user_permissions,
        )
    
    return organization
