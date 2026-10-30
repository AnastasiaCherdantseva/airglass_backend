"""
UseCase: get roles available to the current user.

UseCase: получить роли, доступные текущему пользователю.
"""

import logging
from uuid import UUID

from app.core.exceptions import ConflictError, PermissionDeniedError
from app.dto import (
    CurrentUser,
    RoleWithPermissionsOutput,
)
from app.models.system.permission_condition import ConditionType
from app.repositories.protocols.system import (
    RolePermissionReadRepositoryProtocol,
    RoleReadRepositoryProtocol,
)

logger = logging.getLogger(__name__)
USERS_CREATE = "USERS.CREATE"
ROLES_READ = "ROLES.READ"


async def get_roles(
    actor: CurrentUser,
    *,
    roles: RoleReadRepositoryProtocol,
    role_permissions: RolePermissionReadRepositoryProtocol,
) -> list[RoleWithPermissionsOutput]:
    """
    Get roles available to the actor: assignable via USERS.CREATE and own via ROLES.READ.

    Получить роли, доступные актору: назначаемые через USERS.CREATE и собственные через ROLES.READ.

    Args:
        actor: User performing the request.
        roles: Repository for reading roles.
        role_permissions: Repository for role-condition links.

    Returns:
        Deduplicated roles with permission conditions, sorted with own roles last.

    Args:
        actor: Пользователь, выполняющий запрос.
        roles: Репозиторий чтения ролей.
        role_permissions: Репозиторий связей роль-condition.

    Returns:
        Уникальные роли с условиями, отсортированные так, что собственные — в конце.
    """
    permission_USERS_CREATE = next((p for p in actor.permissions if p.code == USERS_CREATE), None)
    permission_ROLES_READ = next((p for p in actor.permissions if p.code == ROLES_READ), None)

    if permission_USERS_CREATE is None and permission_ROLES_READ is None:
        logger.info("Get roles failed: user (id:%s) has no permission", actor.id)
        raise PermissionDeniedError("Недостаточно прав.")

    result_by_id: dict[UUID, RoleWithPermissionsOutput] = {}

    # USERS.CREATE → роли, которые actor может назначать
    if permission_USERS_CREATE is not None:
        raw_role_ids = {
            c.role_id
            for c in permission_USERS_CREATE.conditions
            if c.is_active is True and c.type == ConditionType.ROLE
        }

        if None in raw_role_ids:
            broken = [c.id for c in permission_USERS_CREATE.conditions if c.role_id is None]
            logger.error(
                "Get roles error: USERS.CREATE condition(s) without role_id: %s",
                broken,
            )
            raise ConflictError("Ошибка сервера.")

        role_ids = [rid for rid in raw_role_ids if rid is not None]
        if role_ids:
            roles_list = await roles.get_by_ids(role_ids)
            conditions = await role_permissions.get_conditions_by_role_ids(role_ids)
            for role in roles_list:
                result_by_id[role.id] = RoleWithPermissionsOutput(
                    id=role.id,
                    name=role.name,
                    owner_id=role.owner_id,
                    description=role.description,
                    is_system=role.is_system,
                    is_active=role.is_active,
                    created_at=role.created_at,
                    updated_at=role.updated_at,
                    permissions=conditions.get(role.id, []),
                )

    # ROLES.READ → собственные роли актора
    if permission_ROLES_READ is not None:
        condition_CREATOR = next(
            (c for c in permission_ROLES_READ.conditions if c.type == ConditionType.CREATOR),
            None,
        )
        if condition_CREATOR is None:
            logger.warning(
                "ROLES.READ without CREATOR condition (actor=%s, conditions=%s)",
                actor.id,
                [(c.id, c.type) for c in permission_ROLES_READ.conditions],
            )
        else:
            own_roles = await roles.get_by_owner_id(actor.id)
            own_role_ids = [r.id for r in own_roles]
            own_conditions = await role_permissions.get_conditions_by_role_ids(own_role_ids)
            for role in own_roles:
                # не перезаписываем, если роль уже добавлена через USERS.CREATE
                if role.id in result_by_id:
                    continue
                result_by_id[role.id] = RoleWithPermissionsOutput(
                    id=role.id,
                    name=role.name,
                    owner_id=role.owner_id,
                    description=role.description,
                    is_system=role.is_system,
                    is_active=role.is_active,
                    created_at=role.created_at,
                    updated_at=role.updated_at,
                    permissions=own_conditions.get(role.id, []),
                )

    result = list(result_by_id.values())
    result.sort(key=lambda r: (r.owner_id == actor.id, r.name, r.id))
    return result
