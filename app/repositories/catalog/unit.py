from sqlalchemy import select

from app.dto.catalog.unit import UnitOutput
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

    async def get_all(self) -> list[UnitOutput]:
        execute = await self.db.execute(select(Unit))
        result = execute.scalars().all()
        return [UnitOutput(id=u.id, name=u.name, symbol=u.symbol) for u in result]
