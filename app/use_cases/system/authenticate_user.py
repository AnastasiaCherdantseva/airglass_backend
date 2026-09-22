"""
UseCase: authenticate a user by email and password.
"""

import logging
from datetime import UTC, datetime

from app.core.exceptions import PermissionDeniedError
from app.core.security import (
    SESSION_TTL,
    generate_session_token,
    hash_session_token,
    is_verified_password,
)
from app.models.system.session import Session
from app.models.system.user import User
from app.repositories.protocols.system.session import SessionWriteRepositoryProtocol
from app.repositories.protocols.system.user import UserReadRepositoryProtocol

logger = logging.getLogger(__name__)


async def authenticate_user(
    email: str,
    password: str,
    *,
    user_agent: str | None = None,
    ip_address: str | None = None,
    sessions: SessionWriteRepositoryProtocol,
    users: UserReadRepositoryProtocol,
) -> tuple[str, User]:
    """
    Authenticate a user by email and password. If successful, create a new session.

    Args:
        email: User email.
        password: Plain-text password.
        user_agent: User device (optional, see ADR-AUTH-002).
        ip_address: User IP address (optional, see ADR-AUTH-002).
        sessions: Session write repository.
        users: Repository for reading users.

    Returns:
        Raw session token for the cookie.

    Raises:
        PermissionDeniedError:
        If credentials are invalid or user is inactive.
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

    token = generate_session_token()
    token_hash = hash_session_token(token)

    now = datetime.now(UTC)

    new_session = Session(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=now + SESSION_TTL,
        last_used_at=now,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    sessions.add(new_session)
    await sessions.flush()

    user_with_toles = 
    return token, user
