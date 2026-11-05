"""
UseCase: delete a role.

UseCase: удалить роль.
"""

import logging
from typing import Any
from uuid import UUID

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.dto import CurrentUser
from app.repositories.protocols.system import (
    RoleRepositoryProtocol,
    UserRoleReadRepositoryProtocol,
)
from app.services.sync_user_permissions import sync_user_permissions

logger = logging.getLogger(__name__)


async def delete_role(
    actor: CurrentUser,
    role_id: UUID,
    *,
    roles: RoleRepositoryProtocol,
    user_roles: UserRoleReadRepositoryProtocol,
    deps_for_sync: dict[str, Any],
) -> None:
    """
    Удалить роль, принадлежащую актору.

    Шаги:
        1. Загрузить роль; если нет -> NotFoundError.
        2. Проверить, что роль не системная -> ValidationError.
        3. Проверить, что актор — владелец роли -> PermissionDeniedError.
        4. Проверить, что роль не единственная у пользователя -> ConflictError.
        5. Собрать id затронутых пользователей.
        6. Удалить роль (каскады БД удалят RolePermission, UserRole,
           PermissionCondition с role_id=role.id и зависимые
           UserDirectPermission / UserPermission).
        7. Синхронизировать user_permissions для каждого затронутого пользователя.

    Args:
        actor: Пользователь, выполняющий операцию.
        role_id: ID роли.
        roles: Репозиторий ролей.
        user_roles: Репозиторий связей пользователь-роль.
        deps_for_sync: Зависимости для ``sync_user_permissions``.

    Raises:
        NotFoundError: Роль не существует.
        ValidationError: Роль системная.
        PermissionDeniedError: Актор не владелец.
        ConflictError: Роль — единственная у хотя бы одного пользователя.
    """
    # 1. Загрузить роль
    role = await roles.get_by_id(role_id)
    if role is None:
        logger.info(
            "Delete role error: role not found (role=%s, actor=%s)",
            role_id,
            actor.id,
        )
        raise NotFoundError("Роль не найдена.")

    # 2. Системную роль удалять нельзя
    if role.is_system:
        logger.info(
            "Delete role error: attempt to delete system role (role=%s, actor=%s)",
            role_id,
            actor.id,
        )
        raise ValidationError("Системную роль удалить нельзя.")

    # 3. Только владелец
    if role.owner_id != actor.id:
        logger.info(
            "Delete role error: actor (%s) is not the owner of role (%s)",
            actor.id,
            role_id,
        )
        raise PermissionDeniedError("Вы не можете удалять чужие роли.")

    # 4. Роль не должна быть единственной у какого-либо пользователя
    user_ids = await user_roles.get_user_ids_by_role_id(role_id)
    for user_id in user_ids:
        user_role_list = await user_roles.get_roles_by_user_id(user_id)
        if len(user_role_list) <= 1:
            logger.info(
                "Delete role error: role (%s) is the only role of user (%s)",
                role_id,
                user_id,
            )
            raise ConflictError(f"Нельзя удалить роль: она единственная у пользователя {user_id}.")

    # 5. Затронутые пользователи (для sync после удаления)
    affected_user_ids = set(user_ids)

    # 6. Удалить роль (каскады БД удалят связи и условия)
    await roles.delete_by_id(role_id)

    logger.info(
        "Role deleted (role=%s, actor=%s, affected_users=%d)",
        role_id,
        actor.id,
        len(affected_user_ids),
    )

    # 7. Пересчитать user_permissions для затронутых пользователей
    for user_id in affected_user_ids:
        await sync_user_permissions(user_id=user_id, **deps_for_sync)
