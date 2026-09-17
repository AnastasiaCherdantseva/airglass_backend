"""
UseCase: create user session.
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import PermissionDeniedError
from app.core.security import SESSION_TTL, generate_session_token, hash_session_token
from app.models.system.session import Session
from app.repositories.protocols.system.session import SessionWriteRepositoryProtocol
from app.repositories.protocols.system.user import UserReadRepositoryProtocol

logger = logging.getLogger(__name__)


async def create_session(
    user_id: UUID,
    *,
    user_agent: str | None,
    ip_address: str | None,
    sessions: SessionWriteRepositoryProtocol,
    users: UserReadRepositoryProtocol,
) -> str:
    """
    Args:
        user_id: User UUID.
        user_agent: User device (optional, see ADR-AUTH-002).
        ip_address: User IP address (optional, see ADR-AUTH-002).
        sessions: Session write repository.
        users: User read repository.

    Returns:
        Raw session token for the cookie.

    Raises:
        PermissionDeniedError: If the user is not found or inactive.
    """
    user = await users.get_by_id(user_id)
    if user is None:
        logger.info("Session create failed: user not found (user_id=%s)", user_id)
        raise PermissionDeniedError("Ошибка входа")
    if not user.is_active:
        logger.info("Session create failed: user inactive (user_id=%s)", user.id)
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
    return token
