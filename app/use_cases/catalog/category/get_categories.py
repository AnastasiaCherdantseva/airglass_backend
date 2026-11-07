import logging

from app.dto.catalog.category import CategoryWithRulesOutput
from app.repositories.protocols.catalog import CategoryReadRepositoryProtocol
from app.repositories.protocols.usage.usage_category_role import (
    CategoryUsageRoleReadRepositoryProtocol,
)

logger = logging.getLogger(__name__)


async def get_categories(
    *,
    categories: CategoryReadRepositoryProtocol,
    category_usage_roles: CategoryUsageRoleReadRepositoryProtocol,
) -> list[CategoryWithRulesOutput]:
    """Get all categories with their attributes, usage roles and media data.

    Получить все категории вместе с атрибутами, ролями использования и данными медиафайлов.

    Args:
        categories: Category repository.
            Репозиторий категорий.
        category_usage_roles: Category-usage-role repository.
            Репозиторий связей категорий с ролями использования.

    Returns:
        Flat list of categories.
            Плоский список категорий.
    """
    categories_data = await categories.get_all()

    if not categories_data:
        return []

    usage_role_ids_by_category = await category_usage_roles.get_usage_role_ids_by_category_ids(
        [category.id for category in categories_data]
    )

    return [
        CategoryWithRulesOutput(
            id=category.id,
            parent_id=category.parent_id,
            name=category.name,
            code=category.code,
            description=category.description,
            sort_order=category.sort_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            attributes_ids=category.attributes_ids,
            usage_role_ids=usage_role_ids_by_category.get(category.id, []),
            media_data=category.media_data,
        )
        for category in categories_data
    ]
