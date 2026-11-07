"""Category catalog router.

Роутер категорий каталога.
"""

from fastapi import APIRouter, Depends, status

from app.core.security_dependencies import get_current_user, require_permission
from app.dto import CurrentUser
from app.repositories.catalog import CategoryRepository
from app.repositories.deps import (
    get_category_repo,
    get_category_usage_role_repo,
)
from app.repositories.usage import CategoryUsageRoleRepository
from app.schemas.catalog.category import CategoryResponse
from app.use_cases.catalog.category.get_categories import get_categories

router = APIRouter(prefix="/categories", tags=["Категории"])

CATEGORY_READ = "CATEGORIES.READ"


@router.get(
    "",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(CATEGORY_READ))],
)
async def get_categories_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    categories: CategoryRepository = Depends(get_category_repo),
    category_usage_roles: CategoryUsageRoleRepository = Depends(get_category_usage_role_repo),
) -> list[CategoryResponse]:
    """Get all categories with their related data.

    Получить все категории вместе со связанными данными.
    """
    result = await get_categories(
        categories=categories,
        category_usage_roles=category_usage_roles,
    )

    return [CategoryResponse.model_validate(category) for category in result]
