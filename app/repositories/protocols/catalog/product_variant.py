from typing import Protocol

from app.models.catalog.product_variant import ProductVariant
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class ProductVariantRepositoryProtocol(
    ReadRepositoryProtocol[ProductVariant],
    WriteRepositoryProtocol[ProductVariant],
    Protocol,
):
    """Repository contract for product variants.

    Контракт репозитория вариаций товаров.
    """

    pass
