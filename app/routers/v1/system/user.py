"""
Users router.

Роутер пользователей.
"""

from fastapi import APIRouter, Depends, status

from app.core.security_dependencies import get_current_user, require_permission
from app.dto import CurrentUser, UserCreate
from app.repositories.deps import (
    get_role_permission_repo,
    get_role_repo,
    get_user_direct_permission_repo,
    get_user_permission_repo,
    get_user_repo,
    get_user_role_repo,
)
from app.repositories.system import (
    RolePermissionRepository,
    RoleRepository,
    UserDirectPermissionRepository,
    UserPermissionRepository,
    UserRepository,
    UserRoleRepository,
)
from app.schemas.system.user import UserCreateRequest, UserWithRolesResponse
from app.use_cases.system.create_user import create_user

router = APIRouter(prefix="/users", tags=["Пользователи"])

# Коды прав
USERS_CREATE = "USERS.CREATE"


@router.post(
    "",
    response_model=UserWithRolesResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(USERS_CREATE))],
)
async def create_user_endpoint(
    body: UserCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    users: UserRepository = Depends(get_user_repo),
    roles: RoleRepository = Depends(get_role_repo),
    user_role: UserRoleRepository = Depends(get_user_role_repo),
    role_permissions: RolePermissionRepository = Depends(get_role_permission_repo),
    user_direct_permissions: UserDirectPermissionRepository = Depends(
        get_user_direct_permission_repo
    ),
    user_permissions: UserPermissionRepository = Depends(get_user_permission_repo),
) -> UserWithRolesResponse:
    """
    Create a user with roles on behalf of the current user.

    Создаёт пользователя с ролями от имени текущего пользователя.
    """
    data = UserCreate(
        email=body.email,
        name=body.name,
        is_active=False,  # BR-USERS-003ы
        password=body.password,
        role_ids=body.role_ids,
    )
    result = await create_user(
        current_user,
        data,
        users=users,
        roles=roles,
        user_role=user_role,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct_permissions,
        user_permissions=user_permissions,
    )
    return UserWithRolesResponse(
        id=result.id,
        email=result.email,
        name=result.name,
        is_active=result.is_active,
        parent_id=result.parent_id,
        role_ids=result.role_ids,
    )
