from app.models.usage.product_usage_role import ProductUsageRole
from app.repositories.base import BaseRepository
from app.repositories.protocols.usage.usage_product_role import (
    ProductUsageRoleReadRepositoryProtocol,
    ProductUsageRoleWriteRepositoryProtocol,
)


class ProductUsageRoleRepository(
    BaseRepository[ProductUsageRole],
    ProductUsageRoleReadRepositoryProtocol,
    ProductUsageRoleWriteRepositoryProtocol,
):
    """Repository for product-usage-role links.

    Репозиторий связей товаров и ролей использования.
    """

    model = ProductUsageRole
