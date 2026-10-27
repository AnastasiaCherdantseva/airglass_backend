"""
Users router.

Роутер пользователей.
"""

from fastapi import APIRouter, Depends, status

from app.core.security_dependencies import get_current_user
from app.dto import CurrentUser
from app.repositories.deps import (
    get_role_permission_repo,
    get_role_repo,
)
from app.repositories.system.role import RoleRepository
from app.repositories.system.role_permission import RolePermissionRepository
from app.schemas.system.role import RoleDetailResponse
from app.use_cases.system.role.get_roles import get_roles

router = APIRouter(prefix="/roles", tags=["Роли"])


@router.get(
    "",
    response_model=list[RoleDetailResponse],
    status_code=status.HTTP_200_OK,
)
async def get_roles_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    roles: RoleRepository = Depends(get_role_repo),
    role_permissions: RolePermissionRepository = Depends(get_role_permission_repo),
) -> list[RoleDetailResponse]:
    """
    Get a paginated list of direct children of the current user.
    """
    result = await get_roles(
        current_user,
        roles=roles,
        role_permissions=role_permissions,
    )
    return [
        RoleDetailResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_active=role.is_active,
            is_system=role.is_system,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=role.permissions,
        )
        for role in result
    ]
