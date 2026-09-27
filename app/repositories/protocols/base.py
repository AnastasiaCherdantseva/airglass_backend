from typing import Protocol, TypeVar
from uuid import UUID

from app.models.base import Base

ModelT_co = TypeVar("ModelT_co", bound=Base, covariant=True)
ModelT_contra = TypeVar("ModelT_contra", bound=Base, contravariant=True)


class ReadRepositoryProtocol(Protocol[ModelT_co]):
    """Контракт чтения из репозитория."""

    async def get_by_id(self, entity_id: UUID) -> ModelT_co | None: ...


class WriteRepositoryProtocol(Protocol[ModelT_contra]):
    """Контракт записи в репозиторий."""

    def add(self, entity: ModelT_contra) -> None: ...
    async def delete(self, entity: ModelT_contra) -> None: ...
    async def delete_by_id(self, entity_id: UUID) -> bool: ...
    async def flush(self) -> None: ...
