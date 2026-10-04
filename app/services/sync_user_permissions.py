"""
UseCase: синхронизация user_permissions для пользователя.
"""

import logging
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.repositories.protocols.system import (
    RolePermissionReadRepositoryProtocol,
    UserDirectPermissionReadRepositoryProtocol,
    UserPermissionWriteRepositoryProtocol,
    UserRoleReadRepositoryProtocol,
)

logger = logging.getLogger(__name__)


async def sync_user_permissions(
    user_id: UUID,
    *,
    user_roles: UserRoleReadRepositoryProtocol,
    role_permissions: RolePermissionReadRepositoryProtocol,
    user_direct_permissions: UserDirectPermissionReadRepositoryProtocol,
    user_permissions: UserPermissionWriteRepositoryProtocol,
) -> None:
    """
    Собрать все condition_id пользователя и записать в user_permissions.

    Шаги:
        1. Активные роли пользователя (BR-ROLE-023).
        2. Conditions из этих ролей.
        3. Direct conditions пользователя.
        4. Объединение через set() — дедупликация.
        5. replace_for_user.

    См. BR-ACCESS-028, ADR-ACCESS-018.
    """
    # 1. Активные роли
    roles = await user_roles.get_roles_by_user_id(user_id)
    if not roles:
        logger.info("Sync user permissions failed: roles for user not found(user: %s)", user_id)
        raise NotFoundError("Не удалось найти роли пользователя.")
    # 2. Conditions из ролей
    conditions_from_roles: list[UUID] = []
    for role in roles:
        role_conditions = await role_permissions.get_condition_ids_by_role_id(role.id)
        conditions_from_roles.extend(role_conditions)

    # 3. Direct conditions
    conditions_from_direct = await user_direct_permissions.get_condition_ids_by_user_id(user_id)

    # 4. Объединение — дедупликация
    all_conditions = list(set(conditions_from_roles + conditions_from_direct))

    # 5. Замена
    await user_permissions.replace_for_user(user_id, all_conditions)

    logger.info(
        "Synced user_permissions (user_id=%s, roles=%d, conditions=%d)",
        user_id,
        len(roles),
        len(all_conditions),
    )
