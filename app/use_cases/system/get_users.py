"""
UseCase: получить пользователя по id.
"""

import logging
from uuid import UUID

from app.dto import UserListOutput, UserWithRolesOutput
from app.repositories.protocols.system.user import UserReadRepositoryProtocol
from app.repositories.protocols.system.user_role import UserRoleReadRepositoryProtocol

logger = logging.getLogger(__name__)


async def get_users(
    owner_id: UUID,
    limit: int,
    page: int,
    *,
    users: UserReadRepositoryProtocol,
    user_roles: UserRoleReadRepositoryProtocol,
) -> UserListOutput | None:
    """
    Получить пользователя по id.

    Бросает NotFoundError, если пользователь не найден.
    """
    children = await users.get_by_parent_id(owner_id, page=page, limit=limit)
    total = await users.count_by_parent_id(owner_id)
    if not children:
        return UserListOutput(items=[], total=total, limit=limit, page=page)

    user_ids = [u.id for u in children]
    users_roles = await user_roles.get_role_ids_by_user_ids(user_ids)
    if len(users_roles.keys()) != len(user_ids):
        for id in user_ids:
            if id not in users_roles.keys():
                logger.warning("User %s has no roles", id)
                users_roles[id] = []
    items = []
    for u in children:
        items.append(
            UserWithRolesOutput(
                id=u.id,
                parent_id=u.parent_id,
                email=u.email,
                name=u.name,
                is_active=u.is_active,
                children_count=u.children_count,
                role_ids=users_roles[u.id],
            )
        )
    return UserListOutput(items=items, total=total, limit=limit, page=page)
