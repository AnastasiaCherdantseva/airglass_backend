from app.models.catalog.unit import Unit
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.unit import (
    UnitReadRepositoryProtocol,
    UnitWriteRepositoryProtocol,
)


class UnitRepository(
    BaseIdRepository[Unit], UnitReadRepositoryProtocol, UnitWriteRepositoryProtocol
):
    """Repository for measurement units.

    Репозиторий единиц измерения.
    """

    model = Unit
