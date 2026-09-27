from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.models import Session
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)
from app.repositories.protocols.dto import (
    SessionInput,
    SessionOutput,
)


class SessionReadRepositoryProtocol(ReadRepositoryProtocol[Session], Protocol):
    """Read Sessions."""

    async def get_by_token_hash(self, token_hash: str) -> Session | None: ...
    async def get_by_user_id(self, user_id: UUID) -> list[Session]: ...


class SessionWriteRepositoryProtocol(WriteRepositoryProtocol[Session], Protocol):
    """Write Sessions."""

    # Массовое удаление по `expires_at` в сравнении с передаваемой датой.
    async def delete_expired(self, time: datetime) -> int: ...

    # Массовое удаление по user_id
    async def delete_by_user_id(self, user_id: UUID) -> int: ...

    # Массовое удаление по user_id
    async def create(self, data: SessionInput) -> SessionOutput: ...

    # Удаление по token_hash
    async def delete_by_token_hash(self, token_hash: str) -> bool: ...


class SessionRepositoryProtocol(
    SessionReadRepositoryProtocol, SessionWriteRepositoryProtocol, Protocol
):
    """Full session repository — read and write."""

    pass
