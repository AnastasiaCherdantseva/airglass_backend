"""
UseCase: получить пользователя по id.
"""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models import User
from app.repositories.protocols.user import UserReadRepositoryProtocol


async def get_user(
    user_id: UUID,
    *,
    users: UserReadRepositoryProtocol,
) -> User:
    """
    Получить пользователя по id.

    Бросает NotFoundError, если пользователь не найден.
    """
    user = await users.get_by_id(user_id)
    if user is None:
        raise NotFoundError(f"Пользователь {user_id} не найден")
    return user
