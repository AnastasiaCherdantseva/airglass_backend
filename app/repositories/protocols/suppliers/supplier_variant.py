from typing import Protocol


class SupplierVariantReadRepositoryProtocol(
    Protocol,
):
    pass


class SupplierVariantWriteRepositoryProtocol(
    Protocol,
):
    pass


class SupplierVariantRepositoryProtocol(
    SupplierVariantReadRepositoryProtocol,
    SupplierVariantWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for supplier product variants.

    Контракт репозитория предложений поставщиков.
    """
