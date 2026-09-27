"""
UseCase: authenticate a user by email and password.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import AuthenticationError
from app.core.security import (
    SESSION_TTL,
    generate_session_token,
    hash_session_token,
    is_verified_password,
)
from app.repositories.protocols.dto import RoleOutput, SessionInput
from app.repositories.protocols.system.session import SessionWriteRepositoryProtocol
from app.repositories.protocols.system.user import UserReadRepositoryProtocol
from app.repositories.protocols.system.user_role import UserRoleReadRepositoryProtocol

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    name: str
    email: str
    session_token: str
    roles: list[RoleOutput]


async def authenticate_user(
    email: str,
    password: str,
    *,
    user_agent: str | None = None,
    ip_address: str | None = None,
    sessions: SessionWriteRepositoryProtocol,
    users: UserReadRepositoryProtocol,
    user_roles: UserRoleReadRepositoryProtocol,
) -> AuthenticatedUser:
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
        AuthenticatedUser: user data, session token and roles.

    Raises:
        AuthenticationError:
        If credentials are invalid or user is inactive.
    """
    user = await users.get_by_email(email)
    if user is None:
        logger.info("Auth failed: user not found")
        raise AuthenticationError("Ошибка входа")

    if not user.is_active:
        logger.info("Auth failed: user inactive (user_id=%s)", user.id)
        raise AuthenticationError("Ошибка входа")

    if not is_verified_password(password, user.password_hash):
        logger.info("Auth failed: wrong password (user_id=%s)", user.id)
        raise AuthenticationError("Ошибка входа")

    token = generate_session_token()
    token_hash = hash_session_token(token)

    now = datetime.now(UTC)

    new_session = SessionInput(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=now + SESSION_TTL,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    await sessions.create(new_session)

    roles = await user_roles.get_roles_by_user_id(user.id)
    return AuthenticatedUser(
        id=user.id, name=user.name, email=user.email, session_token=token, roles=roles
    )
