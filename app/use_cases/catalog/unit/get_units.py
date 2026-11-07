from app.dto.catalog.unit import UnitOutput
from app.repositories.protocols.catalog.unit import UnitReadRepositoryProtocol


async def get_units(
    *,
    units: UnitReadRepositoryProtocol,
) -> list[UnitOutput]:
    return await units.get_all()
