from typing import Protocol


class ProductUsageRoleReadRepositoryProtocol(
    Protocol,
):
    pass


class ProductUsageRoleWriteRepositoryProtocol(
    Protocol,
):
    pass


class ProductUsageRoleRepositoryProtocol(
    ProductUsageRoleReadRepositoryProtocol,
    ProductUsageRoleWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for product-usage-role links.

    Контракт репозитория связей товаров и ролей использования.
    """
