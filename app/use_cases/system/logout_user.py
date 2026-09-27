"""
UseCase: logout a user by token.
"""

import logging

from app.core.security import (
    hash_session_token,
)
from app.repositories.protocols.system.session import SessionWriteRepositoryProtocol

logger = logging.getLogger(__name__)


async def logout_user(
    session_token: str,
    *,
    sessions: SessionWriteRepositoryProtocol,
) -> None:
    token_hash = hash_session_token(session_token)
    result_count = await sessions.delete_by_token_hash(token_hash)

    if result_count == 0:
        logger.info("Logout: session not found (token_hash=%s)", token_hash[:8])
