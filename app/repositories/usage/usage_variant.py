from app.models.usage.variant_usage_role import VariantUsageRole
from app.repositories.base import BaseRepository
from app.repositories.protocols.usage.usage_variant_role import (
    VariantUsageRoleReadRepositoryProtocol,
    VariantUsageRoleWriteRepositoryProtocol,
)


class VariantUsageRoleRepository(
    BaseRepository[VariantUsageRole],
    VariantUsageRoleReadRepositoryProtocol,
    VariantUsageRoleWriteRepositoryProtocol,
):
    """Repository for variant-usage-role links.

    Репозиторий связей вариаций и ролей использования.
    """

    model = VariantUsageRole
