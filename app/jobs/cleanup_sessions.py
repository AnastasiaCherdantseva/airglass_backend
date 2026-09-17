"""
Job: delete expired sessions.
"""

import logging
from datetime import UTC, datetime

from app.core.database import AsyncSessionLocal
from app.repositories.system.session import SessionRepository

logger = logging.getLogger(__name__)


async def cleanup_expired_sessions() -> int:
    """Delete expired sessions. Returns the number deleted."""
    async with AsyncSessionLocal() as session:
        repo = SessionRepository(session)
        deleted = await repo.delete_expired(datetime.now(UTC))
        await session.commit()
        logger.info("Cleanup: deleted %s expired sessions", deleted)
        return deleted
