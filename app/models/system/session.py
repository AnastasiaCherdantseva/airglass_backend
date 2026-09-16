"""
Session model — server-side sessions stored in the database.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.system.user import User


class Session(Base):
    """
    User session.

    Each login creates a new session row. Multiple sessions per user
    are allowed (different devices/browsers).

    The client stores a random token in an httpOnly cookie.
    The server stores only the SHA-256 hash of that token.
    """

    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_session_user_id", "user_id"),
        Index("ix_session_token_hash", "token_hash"),
        Index("ix_session_expires_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    # когда истекает
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
    )
    user_agent: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(45))

    # Связи
    user: Mapped["User"] = relationship()
