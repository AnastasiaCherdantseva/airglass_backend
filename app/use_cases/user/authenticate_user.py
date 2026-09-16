"""
UseCase: authenticate a user by email and password.
"""

import logging

from app.core.exceptions import PermissionDeniedError
from app.core.security import is_verified_password
from app.models.system.user import User
from app.repositories.protocols.user import UserReadRepositoryProtocol

logger = logging.getLogger(__name__)


async def authenticate_user(
    email: str,
    password: str,
    *,
    users: UserReadRepositoryProtocol,
) -> User:
    """
    Authenticate a user by email and password.

    Args:
        email: User email.
        password: Plain-text password.
        users: Repository for reading users.

    Returns:
        The authenticated user.

    Raises:
        PermissionDeniedError: If credentials are invalid or user is inactive.
    """
    user = await users.get_by_email(email)
    if user is None:
        logger.info("Auth failed: user not found ")
        raise PermissionDeniedError("Ошибка входа")

    if not user.is_active:
        logger.info("Auth failed: user inactive (user_id=%s)", user.id)
        raise PermissionDeniedError("Ошибка входа")

    if not is_verified_password(password, user.password_hash):
        logger.info("Auth failed: wrong password (user_id=%s)", user.id)
        raise PermissionDeniedError("Ошибка входа")

    return user
