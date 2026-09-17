"""
Pydantic schemas for sessions.
"""

from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class SessionResponse(BaseSchema):
    """Session info returned to the client."""

    id: UUID
    user_agent: str | None
    ip_address: str | None
    created_at: datetime
    last_used_at: datetime | None
    is_current: bool = False  # вычисляется на стороне роутера
