from fastapi import APIRouter, Depends, status

from app.core.security_dependencies import get_current_user
from app.dto import CurrentUser
from app.repositories.deps import (
    get_usage_role_repo,
)
from app.repositories.usage.usage_role import UsageRoleRepository
from app.schemas import UsageRoleResponse
from app.use_cases.usage import get_usage_roles

router = APIRouter(prefix="/usage_roles", tags=["Роли использования"])


@router.get(
    "",
    response_model=list[UsageRoleResponse],
    status_code=status.HTTP_200_OK,
)
async def get_usage_roles_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    usage_roles: UsageRoleRepository = Depends(get_usage_role_repo),
) -> list[UsageRoleResponse]:
    result = await get_usage_roles(
        usage_roles=usage_roles,
    )

    return [UsageRoleResponse(id=ur.id, name=ur.name, description=ur.description) for ur in result]
