from app.models.attributes.category_attribute import CategoryAttribute
from app.repositories.base import BaseRepository
from app.repositories.protocols.catalog.category_attributes import (
    CategoryAttributeReadRepositoryProtocol,
    CategoryAttributeWriteRepositoryProtocol,
)


class CategoryAttributeRepository(
    BaseRepository[CategoryAttribute],
    CategoryAttributeReadRepositoryProtocol,
    CategoryAttributeWriteRepositoryProtocol,
):
    """Repository for category-attribute links.

    Репозиторий связей категорий и атрибутов.
    """

    model = CategoryAttribute
