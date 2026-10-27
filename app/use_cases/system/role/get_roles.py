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
from app.repositories.protocols.system import (
    RolePermissionReadRepositoryProtocol,
    RoleReadRepositoryProtocol,
)

logger = logging.getLogger(__name__)
ROLES_READ = "ROLES.READ"


async def get_roles(
    actor: CurrentUser,
    *,
    roles: RoleReadRepositoryProtocol,
    role_permissions: RolePermissionReadRepositoryProtocol,
) -> list[RoleWithPermissionsOutput]:
    """
    Get roles created by or assigned to the actor, including inactive ones.

    Args:
        actor: User performing the request.
        roles: Repository for reading roles.
        user_roles: Repository for user-role links.
        role_permissions: Repository for role-condition links.
        permission_conditions: Repository for reading permission conditions.

    Returns:
        Unique roles with their permission conditions. Roles owned by
        others (and system roles) come first, the actor's own roles last;
        within each group sorted  by id.

    Raises:
        PermissionDeniedError: Actor has no active ALLOW for ROLES.READ.

    Получить роли, созданные актором или назначенные ему, включая
    неактивные.

    Args:
        actor: Пользователь, выполняющий запрос.
        roles: Репозиторий чтения ролей.
        user_roles: Репозиторий связей пользователь-роль.
        role_permissions: Репозиторий связей роль-condition.
        permission_conditions: Репозиторий чтения вариантов прав.

    Returns:
        Уникальные роли с их conditions. Сначала чужие и системные роли,
        затем собственные; внутри группы по name, затем по id.

    Raises:
        PermissionDeniedError: У актора нет активного ALLOW на ROLES.READ.
    """
    permission = next((p for p in actor.permissions if p.code == ROLES_READ), None)

    if permission is None:
        logger.info("Get roles failed: user (id:%s) have not permission", actor.id)
        raise PermissionDeniedError("Недостаточно прав.")

    raw_role_ids = {c.role_id for c in permission.conditions if c.is_active is True}

    if None in raw_role_ids:
        broken = [c.id for c in permission.conditions if c.role_id is None]

        logger.error(
            "Get roles error: any condition (ids: %s) has no role_id but it has relationship with permission with code ROLES.READ",
            broken,
        )
        raise ConflictError("Ошибка сервера.")

    role_ids: list[UUID] = [rid for rid in raw_role_ids if rid is not None]
    roles_list = await roles.get_by_ids(role_ids)
    conditions = await role_permissions.get_conditions_by_role_ids(role_ids)
    result = [
        RoleWithPermissionsOutput(
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
        for role in roles_list
    ]
    # False < True: не собственные первыми, собственные последними.
    result.sort(key=lambda r: (r.owner_id == actor.id, r.id))
    return result
