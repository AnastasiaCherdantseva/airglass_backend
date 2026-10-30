"""
UseCase: get roles available to the current user.

UseCase: получить роли, доступные текущему пользователю.
"""

import logging
from uuid import UUID

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
    RoleWriteRepositoryProtocol,
    PermissionReadRepositoryProtocol
)

logger = logging.getLogger(__name__)
USERS_CREATE = "USERS.CREATE"
ROLES_READ = "ROLES.READ"


async def create_role(
    actor: CurrentUser,
    data: RoleCreate,
    *,
    roles: RoleWriteRepositoryProtocol,
    role_permissions: RolePermissionRepositoryProtocol,
    permissions: PermissionReadRepositoryProtocol,
) -> RoleWithPermissionsOutput:
    
    actorConditionIds = set()
    for permission in actor.permissions:
        for condition in permission.conditions:
            actorConditionIds.add(condition.id)
    missing = actorConditionIds - set(data.conditions)
    if missing:
        logger.info(
            "Create role error: actor with id (%s) try ro create role with conditions (%s) but he has not this coditions",
            actor.id,
            missing,
        )
        raise PermissionDeniedError(f"Недостаточно прав.")

    new_role = await roles.create(data)

    conditions_for_role_count = await role_permissions.add_links_for_role(new_role.id, data.conditions)
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
        conds_ids_set = set(conds_ids)
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
        is_active=-new_role.is_active,
        id=new_role.id,
        created_at=new_role.created_at,
        updated_at=new_role.updated_at,
        permissions=grouped
    )
    