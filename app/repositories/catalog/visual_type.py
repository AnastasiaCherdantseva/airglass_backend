from app.models.catalog.visual_type import VisualType
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.visual_type import (
    VisualTypeReadRepositoryProtocol,
    VisualTypeWriteRepositoryProtocol,
)


class VisualTypeRepository(
    BaseIdRepository[VisualType],
    VisualTypeReadRepositoryProtocol,
    VisualTypeWriteRepositoryProtocol,
):
    """Repository for visual types.

    Репозиторий типов визуализации.
    """

    model = VisualType
