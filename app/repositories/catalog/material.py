from app.models.catalog.material import Material
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.material import (
    MaterialReadRepositoryProtocol,
    MaterialWriteRepositoryProtocol,
)


class MaterialRepository(
    BaseIdRepository[Material], MaterialReadRepositoryProtocol, MaterialWriteRepositoryProtocol
):
    """Repository for materials.

    Репозиторий материалов.
    """

    model = Material
