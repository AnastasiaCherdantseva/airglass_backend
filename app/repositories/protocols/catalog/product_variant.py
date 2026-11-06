from typing import Protocol

from app.models.catalog.product_variant import ProductVariant
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class ProductVariantReadRepositoryProtocol(
    ReadRepositoryProtocol[ProductVariant],
    Protocol,
):
    pass


class ProductVariantWriteRepositoryProtocol(
    WriteRepositoryProtocol[ProductVariant],
    Protocol,
):
    pass


class ProductVariantRepositoryProtocol(
    ProductVariantReadRepositoryProtocol,
    ProductVariantWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for product variants.

    Контракт репозитория вариаций товаров.
    """

    pass
