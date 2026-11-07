"""Category catalog router.

Роутер категорий каталога.
"""

from fastapi import APIRouter, Depends, status

from app.core.security_dependencies import get_current_user
from app.dto import CurrentUser
from app.repositories.catalog.unit import UnitRepository
from app.repositories.deps import (
    get_unit_repo,
)
from app.schemas.catalog.unit import UnitResponse
from app.use_cases.catalog.unit.get_units import get_units

router = APIRouter(prefix="/units", tags=["Типы значений"])


@router.get(
    "",
    response_model=list[UnitResponse],
    status_code=status.HTTP_200_OK,
)
async def get_units_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    units: UnitRepository = Depends(get_unit_repo),
) -> list[UnitResponse]:
    """Get all categories with their related data.

    Получить все категории вместе со связанными данными.
    """
    result = await get_units(
        units=units,
    )

    return [UnitResponse(id=u.id, name=u.name, symbol=u.symbol) for u in result]
