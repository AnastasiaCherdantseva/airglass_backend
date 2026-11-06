from typing import Protocol

from app.dto.catalog.category import CategoryOutput
from app.models.catalog.category import Category
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class CategoryReadRepositoryProtocol(ReadRepositoryProtocol[Category], Protocol):
    """Read contract for categories.

    Контракт чтения категорий.
    """

    async def get_all(self) -> list[CategoryOutput]:
        """Get all non-deleted categories with attribute IDs.

        Получить все неудалённые категории вместе с ID атрибутов.
        """
        ...


class CategoryWriteRepositoryProtocol(WriteRepositoryProtocol[Category], Protocol):
    """Write contract for categories.

    Контракт записи категорий.
    """

    pass


class CategoryRepositoryProtocol(
    CategoryReadRepositoryProtocol,
    CategoryWriteRepositoryProtocol,
    Protocol,
):
    """Full category repository contract.

    Полный контракт репозитория категорий.
    """

    pass
