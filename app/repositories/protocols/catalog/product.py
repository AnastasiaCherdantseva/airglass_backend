from typing import Protocol

from app.models.catalog.product import Product
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class ProductReadRepositoryProtocol(
    ReadRepositoryProtocol[Product],
    Protocol,
):
    pass


class ProductWriteRepositoryProtocol(
    WriteRepositoryProtocol[Product],
    Protocol,
):
    pass


class ProductRepositoryProtocol(
    ProductReadRepositoryProtocol,
    ProductWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for products.

    Контракт репозитория товаров.
    """

    pass
