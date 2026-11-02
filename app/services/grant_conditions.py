"""
Grant permission conditions to a user directly.

Выдать условия прав пользователю напрямую.
"""

import logging
from uuid import UUID

from app.repositories.protocols.system import (
    UserDirectPermissionWriteRepositoryProtocol,
    UserPermissionWriteRepositoryProtocol,
)

logger = logging.getLogger(__name__)


async def grant_conditions_to_user(
    user_id: UUID,
    condition_ids: list[UUID],
    *,
    user_direct_permissions: UserDirectPermissionWriteRepositoryProtocol,
    user_permissions: UserPermissionWriteRepositoryProtocol,
) -> None:
    """
    Выдать существующие условия пользователю напрямую.

    Создаёт ``UserDirectPermission`` и ``UserPermission``.
    Не проверяет, что у пользователя есть доступ к условиям, и не
    вызывает ``sync_user_permissions`` — валидация на стороне
    вызывающего кода.

    Args:
        user_id: Целевой пользователь.
        condition_ids: ID существующих условий для выдачи.
        user_direct_permissions: Репозиторий прямых прав.
        user_permissions: Репозиторий эффективных прав.
    """
    if not condition_ids:
        return

    await user_direct_permissions.add_links(user_id, condition_ids)
    await user_permissions.add_links(user_id, condition_ids)

    logger.info(
        "Granted conditions to user (user_id=%s, count=%d)",
        user_id,
        len(condition_ids),
    )
