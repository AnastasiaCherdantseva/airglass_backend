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
