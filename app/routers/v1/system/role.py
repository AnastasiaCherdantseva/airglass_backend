"""
Users router.

Роутер пользователей.
"""

from fastapi import APIRouter, Depends, status

from app.core.security_dependencies import (
    get_current_user,
    require_permission,
)
from app.dto import CurrentUser, RoleCreate
from app.repositories.deps import (
    get_permission_condition_repo,
    get_role_permission_repo,
    get_role_repo,
    get_user_direct_permission_repo,
    get_user_permission_repo,
)
from app.repositories.system import (
    PermissionConditionRepository,
    RolePermissionRepository,
    RoleRepository,
)
from app.repositories.system.user_direct_permission import UserDirectPermissionRepository
from app.repositories.system.user_permission import UserPermissionRepository
from app.schemas.system.role import RoleCreateRequest, RoleDetailResponse
from app.use_cases.system import create_role, get_roles

router = APIRouter(prefix="/roles", tags=["Роли"])

ROLES_CREATE = "ROLES.CREATE"


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
            owner_id=role.owner_id,
            is_active=role.is_active,
            is_system=role.is_system,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=role.permissions,
        )
        for role in result
    ]


@router.post(
    "",
    response_model=RoleDetailResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(ROLES_CREATE))],
)
async def create_role_endpoint(
    body: RoleCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    roles: RoleRepository = Depends(get_role_repo),
    role_permissions: RolePermissionRepository = Depends(get_role_permission_repo),
    permission_conditions: PermissionConditionRepository = Depends(get_permission_condition_repo),
    user_direct_permissions: UserDirectPermissionRepository = Depends(
        get_user_direct_permission_repo
    ),
    user_permissions: UserPermissionRepository = Depends(get_user_permission_repo),
) -> RoleDetailResponse:
    """Create a role owned by the current user.

    Создаёт роль, владельцем которой становится текущий пользователь.
    """
    data = RoleCreate(
        name=body.name,
        owner_id=current_user.id,
        description=body.description,
        conditions=body.condition_ids,
        is_active=body.is_active,
    )
    role = await create_role(
        current_user,
        data,
        roles=roles,
        role_permissions=role_permissions,
        permission_conditions=permission_conditions,
        user_direct_permissions=user_direct_permissions,
        user_permissions=user_permissions,
    )
    return RoleDetailResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        owner_id=role.owner_id,
        is_active=role.is_active,
        is_system=role.is_system,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=role.permissions,
    )
