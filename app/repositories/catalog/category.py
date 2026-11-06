from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dto.catalog.category import CategoryOutput
from app.models.catalog.category import Category
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.category import (
    CategoryReadRepositoryProtocol,
    CategoryWriteRepositoryProtocol,
)


class CategoryRepository(
    BaseIdRepository[Category], CategoryReadRepositoryProtocol, CategoryWriteRepositoryProtocol
):
    """Repository for categories.

    Репозиторий категорий.
    """

    model = Category

    async def get_all(self) -> list[CategoryOutput]:
        """Get all non-deleted categories with their attribute IDs.

        Получить все неудалённые категории вместе с ID их атрибутов.
        """
        stmt = (
            select(Category)
            .options(selectinload(Category.category_attributes))
            .where(Category.deleted_at.is_(None))
            .order_by(Category.sort_order, Category.name, Category.id)
        )
        result = await self.db.execute(stmt)
        categories = result.scalars().all()

        return [
            CategoryOutput(
                id=category.id,
                parent_id=category.parent_id,
                name=category.name,
                code=category.code,
                description=category.description,
                sort_order=category.sort_order,
                is_active=category.is_active,
                created_at=category.created_at,
                updated_at=category.updated_at,
                attributes_ids=[link.attribute_id for link in category.category_attributes],
            )
            for category in categories
        ]
