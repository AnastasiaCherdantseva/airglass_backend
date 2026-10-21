"""
Delete a user and their entire descendant subtree.

Удаление пользователя и всего его дочернего поддерева.
"""

import logging
from uuid import UUID

from app.core.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.dto import CurrentUser
from app.repositories.protocols.system import (
    OrganizationRepositoryProtocol,
    RoleRepositoryProtocol,
    SessionRepositoryProtocol,
    UserOrganizationWriteRepositoryProtocol,
    UserRepositoryProtocol,
)
from app.repositories.protocols.system.user_direct_permission import (
    UserDirectPermissionWriteRepositoryProtocol,
)
from app.repositories.protocols.system.user_permission import UserPermissionWriteRepositoryProtocol
from app.repositories.protocols.system.user_role import (
    UserRoleWriteRepositoryProtocol,
)

logger = logging.getLogger(__name__)


async def delete_user(
    actor: CurrentUser,
    user_id: UUID,
    *,
    users: UserRepositoryProtocol,
    roles: RoleRepositoryProtocol,
    organizations: OrganizationRepositoryProtocol,
    user_roles: UserRoleWriteRepositoryProtocol,
    user_organizations: UserOrganizationWriteRepositoryProtocol,
    user_direct_permissions: UserDirectPermissionWriteRepositoryProtocol,
    user_permissions: UserPermissionWriteRepositoryProtocol,
    sessions: SessionRepositoryProtocol,
) -> None:
    """
    Soft-delete a user and all descendants, removing dependent data.

    Args:
        actor: User performing the deletion.
        user_id: ID of the target user.
        users: User repository.
        roles: Role repository.
        organizations: Organization repository.
        user_roles: User-role link repository.
        user_organizations: User-organization link repository.
        user_direct_permissions: Direct permission repository.
        user_permissions: Effective permission repository.
        sessions: Session repository.

    Raises:
        NotFoundError: Target user does not exist.
        ValidationError: Actor attempts to delete themselves or
            the hierarchy is inconsistent.
        PermissionDeniedError: Target is outside actor's subtree.

    """
    target = await users.get_by_id(user_id)

    if target is None:
        logger.info(
            "User deletion failed: user not found (user=%s, actor=%s)",
            user_id,
            actor.id,
        )
        raise NotFoundError("Пользователь не найден.")

    if target.id == actor.id:
        logger.info(
            "User deletion failed: self-deletion denied (actor=%s)",
            actor.id,
        )
        raise ValidationError("Нельзя удалить самого себя.")

    in_subtree = await users.is_in_subtree(actor.id, user_id)
    if not in_subtree:
        logger.info(
            "User deletion denied: target is outside actor subtree (target=%s, actor=%s)",
            target.id,
            actor.id,
        )
        raise PermissionDeniedError("Можно удалять только пользователей своего поддерева.")

    subtree = await users.get_subtree(user_id)
    subtree_ids_list = [c.id for c in subtree]

    await user_organizations.remove_by_user_ids(subtree_ids_list)
    await user_roles.remove_by_user_ids(subtree_ids_list)
    await user_direct_permissions.remove_by_user_ids(subtree_ids_list)
    await user_permissions.delete_by_user_ids(subtree_ids_list)

    await roles.delete_by_owner_ids(subtree_ids_list)
    await organizations.delete_by_owner_ids(subtree_ids_list)

    await sessions.delete_by_user_ids(subtree_ids_list)
    await users.soft_delete_by_id(user_id)
