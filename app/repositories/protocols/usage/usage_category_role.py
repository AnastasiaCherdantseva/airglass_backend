from typing import Protocol


class CategoryUsageRoleReadRepositoryProtocol(
    Protocol,
):
    pass


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
