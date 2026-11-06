from app.repositories.protocols.usage.usage_category_role import (
    CategoryUsageRoleReadRepositoryProtocol,
    CategoryUsageRoleRepositoryProtocol,
    CategoryUsageRoleWriteRepositoryProtocol,
)
from app.repositories.protocols.usage.usage_product_role import (
    ProductUsageRoleReadRepositoryProtocol,
    ProductUsageRoleRepositoryProtocol,
    ProductUsageRoleWriteRepositoryProtocol,
)
from app.repositories.protocols.usage.usage_role import (
    UsageRoleReadRepositoryProtocol,
    UsageRoleRepositoryProtocol,
    UsageRoleWriteRepositoryProtocol,
)
from app.repositories.protocols.usage.usage_variant_role import (
    VariantUsageRoleReadRepositoryProtocol,
    VariantUsageRoleRepositoryProtocol,
    VariantUsageRoleWriteRepositoryProtocol,
)

__all__ = [
    "CategoryUsageRoleRepositoryProtocol",
    "CategoryUsageRoleWriteRepositoryProtocol",
    "CategoryUsageRoleReadRepositoryProtocol",
    "ProductUsageRoleRepositoryProtocol",
    "ProductUsageRoleWriteRepositoryProtocol",
    "ProductUsageRoleReadRepositoryProtocol",
    "UsageRoleRepositoryProtocol",
    "UsageRoleWriteRepositoryProtocol",
    "UsageRoleReadRepositoryProtocol",
    "VariantUsageRoleRepositoryProtocol",
    "VariantUsageRoleWriteRepositoryProtocol",
    "VariantUsageRoleReadRepositoryProtocol",
]
