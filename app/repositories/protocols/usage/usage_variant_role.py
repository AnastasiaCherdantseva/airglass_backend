from typing import Protocol


class VariantUsageRoleReadRepositoryProtocol(
    Protocol,
):
    pass


class VariantUsageRoleWriteRepositoryProtocol(
    Protocol,
):
    pass


class VariantUsageRoleRepositoryProtocol(
    VariantUsageRoleReadRepositoryProtocol,
    VariantUsageRoleWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for variant-usage-role links.

    Контракт репозитория связей вариаций и ролей использования.
    """
