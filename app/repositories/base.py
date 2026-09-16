# app/repositories/base.py
from typing import ClassVar, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Для моделей с составным PK — только add/delete/flush."""

    model: ClassVar[type[ModelT]]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def add(self, entity: ModelT) -> None:
        self.db.add(entity)

    async def delete(self, entity: ModelT) -> None:
        await self.db.delete(entity)

    async def flush(self) -> None:
        await self.db.flush()


class BaseIdRepository(BaseRepository[ModelT]):
    """Для моделей с полем id — добавляет get_by_id."""

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()