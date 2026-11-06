from typing import Protocol

from app.models.catalog.product import Product
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class ProductRepositoryProtocol(
    ReadRepositoryProtocol[Product],
    WriteRepositoryProtocol[Product],
    Protocol,
):
    """Repository contract for products.

    Контракт репозитория товаров.
    """

    pass
