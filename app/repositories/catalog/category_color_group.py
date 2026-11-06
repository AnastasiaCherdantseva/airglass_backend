from app.models.catalog.category_color_group import CategoryColorGroup
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.category_color_group import (
    CategoryColorGroupReadRepositoryProtocol,
    CategoryColorGroupWriteRepositoryProtocol,
)


class CategoryColorGroupRepository(
    BaseIdRepository[CategoryColorGroup],
    CategoryColorGroupReadRepositoryProtocol,
    CategoryColorGroupWriteRepositoryProtocol,
):
    """Repository for category-color-group links.

    Репозиторий связей категорий и групп цветов.
    """

    model = CategoryColorGroup
