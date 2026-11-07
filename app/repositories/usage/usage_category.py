from collections import defaultdict
from uuid import UUID

from sqlalchemy import select

from app.models.usage.category_usage_role import CategoryUsageRole
from app.repositories.base import BaseRepository
from app.repositories.protocols.usage.usage_category_role import (
    CategoryUsageRoleReadRepositoryProtocol,
    CategoryUsageRoleWriteRepositoryProtocol,
)


class CategoryUsageRoleRepository(
    BaseRepository[CategoryUsageRole],
    CategoryUsageRoleReadRepositoryProtocol,
    CategoryUsageRoleWriteRepositoryProtocol,
):
    """Repository for category-usage-role links.

    Репозиторий связей категорий и ролей использования.
    """

    model = CategoryUsageRole

    async def get_usage_role_ids_by_category_id(
        self,
        category_id: UUID,
    ) -> list[UUID]:
        """Get usage role IDs assigned to a category.

        Получить ID ролей использования, назначенных категории.
        """
        stmt = select(CategoryUsageRole.usage_role_id).where(
            CategoryUsageRole.category_id == category_id
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_usage_role_ids_by_category_ids(
        self,
        category_ids: list[UUID],
    ) -> dict[UUID, list[UUID]]:
        """Get usage role IDs grouped by category IDs.

        Получить ID ролей использования, сгруппированные по ID категорий.
        """
        if not category_ids:
            return {}

        stmt = select(
            CategoryUsageRole.category_id,
            CategoryUsageRole.usage_role_id,
        ).where(CategoryUsageRole.category_id.in_(category_ids))

        result = await self.db.execute(stmt)

        usage_role_ids: dict[UUID, list[UUID]] = defaultdict(list)

        for category_id, usage_role_id in result.all():
            usage_role_ids[category_id].append(usage_role_id)

        return dict(usage_role_ids)
