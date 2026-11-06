from app.models.catalog.category_material_group import CategoryMaterialGroup
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.category_material_group import (
    CategoryMaterialGroupReadRepositoryProtocol,
    CategoryMaterialGroupWriteRepositoryProtocol,
)


class CategoryMaterialGroupRepository(
    BaseIdRepository[CategoryMaterialGroup],
    CategoryMaterialGroupReadRepositoryProtocol,
    CategoryMaterialGroupWriteRepositoryProtocol,
):
    """Repository for category-material-group links.

    Репозиторий связей категорий и групп материалов.
    """

    model = CategoryMaterialGroup
