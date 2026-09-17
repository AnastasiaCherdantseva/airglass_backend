from typing import Protocol
from uuid import UUID

from app.models import Session
from app.repositories.protocols.base import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)


class SessionReadRepositoryProtocol(ReadRepositoryProtocol[Session], Protocol):
    """Read Sessions."""

    async def get_by_token(self, token: str) -> Session | None: ...


class SessionWriteRepositoryProtocol(WriteRepositoryProtocol[Session], Protocol):
    """Write Sessions."""

    async def create(
        self, *, user_id: UUID, user_agent: str | None, ip_address: str | None
    ) -> str | None: ...


class SessionRepositoryProtocol(
    SessionReadRepositoryProtocol, SessionWriteRepositoryProtocol, Protocol
):
    """Full session repository — read and write."""

    pass
