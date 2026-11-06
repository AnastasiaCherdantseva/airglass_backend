from app.models.catalog.material_group import MaterialGroup
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.material_group import (
    MaterialGroupReadRepositoryProtocol,
    MaterialGroupWriteRepositoryProtocol,
)


class MaterialGroupRepository(
    BaseIdRepository[MaterialGroup],
    MaterialGroupReadRepositoryProtocol,
    MaterialGroupWriteRepositoryProtocol,
):
    """Repository for material groups.

    Репозиторий групп материалов.
    """

    model = MaterialGroup
