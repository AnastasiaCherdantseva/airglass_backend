from typing import Protocol


class SupplierVariantPriceReadRepositoryProtocol(
    Protocol,
):
    pass


class SupplierVariantPriceWriteRepositoryProtocol(
    Protocol,
):
    pass


class SupplierVariantPriceRepositoryProtocol(
    SupplierVariantPriceReadRepositoryProtocol,
    SupplierVariantPriceWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for supplier variant price history.

    Контракт репозитория истории цен предложений поставщиков.
    """
