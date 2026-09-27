from dataclasses import dataclass
from datetime import datetime  # ← класс
from uuid import UUID


@dataclass(frozen=True)
class SessionData:
    user_id: UUID
    user_agent: str | None
    ip_address: str | None
    token_hash: str


@dataclass(frozen=True)
class SessionInput(SessionData):
    expires_at: datetime


@dataclass(frozen=True)
class SessionOutput(SessionData):
    expires_at: datetime
    id: UUID
