from typing import Protocol
from uuid import UUID


class CategoryUsageRoleReadRepositoryProtocol(
    Protocol,
):
    async def get_usage_role_ids_by_category_id(
        self,
        category_id: UUID,
    ) -> list[UUID]:
        """Get usage role IDs assigned to a category.

        Получить ID ролей использования, назначенных категории.
        """
        ...

    async def get_usage_role_ids_by_category_ids(
        self,
        category_ids: list[UUID],
    ) -> dict[UUID, list[UUID]]: ...


class CategoryUsageRoleWriteRepositoryProtocol(
    Protocol,
):
    pass


class CategoryUsageRoleRepositoryProtocol(
    CategoryUsageRoleReadRepositoryProtocol,
    CategoryUsageRoleWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for category-usage-role links.

    Контракт репозитория связей категорий и ролей использования.
    """
