"""
UseCase: get roles available to the current user.

UseCase: получить роли, доступные текущему пользователю.
"""

import logging
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import ConflictError, PermissionDeniedError, ValidationError
from app.dto import (
    CurrentUser,
    RoleWithPermissionsOutput,
)
from app.dto.system.permission_condition import PermissionConditionAllOutPut
from app.dto.system.role import RoleCreate
from app.dto.system.user_permission import GroupedPermission
from app.models.system.permission_condition import ConditionType
from app.repositories.protocols.system import (
    RolePermissionRepositoryProtocol,
    RoleRepositoryProtocol,
    PermissionReadRepositoryProtocol
)

logger = logging.getLogger(__name__)


async def create_role(
    actor: CurrentUser,
    data: RoleCreate,
    *,
    roles: RoleRepositoryProtocol,
    role_permissions: RolePermissionRepositoryProtocol,
    permissions: PermissionReadRepositoryProtocol,
) -> RoleWithPermissionsOutput:
    if actor.id != data.owner_id:
        logger.info(
            "Create role error: actor with id (%s) try to create role with another owner id (%s)",
            actor.id,
            data.owner_id,
        )
        raise ValidationError(f"Вы не можете создавать роли не пренадлежащие вам.")
    
    actor_condition_ids = {
        condition.id
        for permission in actor.permissions
        for condition in permission.conditions
    }
    requested = set(data.conditions)
    foreign = requested - actor_condition_ids
    if foreign:
        logger.info(
            "Create role error: actor (id=%s) tried to use conditions he has no access to: %s",
            actor.id,
            foreign,
        )
        raise PermissionDeniedError("Недостаточно прав.")
    
    normalise_name = data.name.strip().capitalize()
    data.name = normalise_name

    try:
        new_role = await roles.create(data)
        conditions_for_role_count = await role_permissions.add_links_for_role(new_role.id, data.conditions)
    except IntegrityError as exc:
        constraint_name = (
            getattr(exc.orig, "constraint_name", None)
            or getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
            or getattr(getattr(exc.orig, "__cause__", None), "constraint_name", "")
        )
        if constraint_name == "uq_role_owner_name":
            logger.info(
                "Create role error: actor with id (%s) already has role with name %s",
                data.owner_id,
                data.name,
            )
            raise ConflictError(f"У вас уже существует роль с таким именем.")
        logger.exception("Unexpected IntegrityError in create_organization")
        raise ConflictError("Не удалось создать роль.") from exc


    if conditions_for_role_count < len(data.conditions):
        logger.info(
            "Create role error: added %s relationships for role&conds, but It was expected %s.",
            conditions_for_role_count,
            len(data.conditions),
        )
        raise ConflictError(f"Не удалось добавить все права к роли.")

    perms_for_conds = await permissions.get_by_conditions(data.conditions)

    actor_perms_by_id: dict[UUID, GroupedPermission] = {
        p.id: p for p in actor.permissions
    }
    grouped = []
    for permission, conds_ids in  perms_for_conds.items():
        src = actor_perms_by_id.get(permission.id)
        if src is None:
            continue
        conds_ids_set = set(data.conditions)
        filtered = [c for c in src.conditions if c.id in conds_ids_set]
        if filtered:
            grouped.append(
                GroupedPermission(
                    id=permission.id,
                    code=permission.code,
                    conditions=filtered,
                )
            )
    return RoleWithPermissionsOutput(
        name=new_role.name,
        owner_id=new_role.owner_id,
        description=new_role.description,
        is_system=new_role.is_system,
        is_active=new_role.is_active,
        id=new_role.id,
        created_at=new_role.created_at,
        updated_at=new_role.updated_at,
        permissions=grouped
    )
    