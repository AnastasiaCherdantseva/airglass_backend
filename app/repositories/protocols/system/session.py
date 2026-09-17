from typing import Protocol

from app.models import Session
from app.repositories.protocols.base import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)


class SessionReadRepositoryProtocol(ReadRepositoryProtocol[Session], Protocol):
    """Read Sessions."""

    async def get_by_token(self, token: str) -> Session | None: ...

    pass


class SessionWriteRepositoryProtocol(WriteRepositoryProtocol[Session], Protocol):
    """Write Sessions."""

    pass
