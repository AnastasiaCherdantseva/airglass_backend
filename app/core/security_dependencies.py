"""
FastAPI dependencies for authentication.
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Cookie, Depends

from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import (
    SESSION_COOKIE_NAME,
    SESSION_TTL,
    hash_session_token,
    user_has_permission,
)
from app.dto import CurrentUser
from app.repositories.deps import (
    get_permission_condition_repo,
    get_permission_repo,
    get_role_permission_repo,
    get_session_repo,
    get_user_direct_permission_repo,
    get_user_organization_repo,
    get_user_permission_repo,
    get_user_repo,
    get_user_role_repo,
)
from app.repositories.system import SessionRepository, UserPermissionRepository, UserRepository
from app.repositories.system.permission import PermissionRepository
from app.repositories.system.role_permission import RolePermissionRepository
from app.repositories.system.user_direct_permission import UserDirectPermissionRepository
from app.repositories.system.user_role import UserRoleRepository

SESSION_EXTEND_INTERVAL = timedelta(hours=24)


async def get_current_user(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    sessions: SessionRepository = Depends(get_session_repo),
    users: UserRepository = Depends(get_user_repo),
    user_permissions: UserPermissionRepository = Depends(get_user_permission_repo),
) -> CurrentUser:
    """
    Resolve the current user from the session cookie.

    Steps:
        1. Read the session token from the cookie (BR-AUTH-016).
        2. Hash it and find the session in the DB (ADR-AUTH-008).
        3. Check the session is not expired (BR-AUTH-013).
        4. Extend the session if needed (BR-AUTH-011).
        5. Load the user and verify access (ADR-USER-004).

    Raises:
        AuthenticationError: 401 if any check fails.
    """
    if session_token is None:
        raise AuthenticationError("Не аутентифицирован")

    token_hash = hash_session_token(session_token)
    session = await sessions.get_by_token_hash(token_hash)
    if session is None:
        raise AuthenticationError("Не аутентифицирован")

    now = datetime.now(UTC)

    if session.expires_at < now:
        await sessions.delete_by_token_hash(token_hash)
        raise AuthenticationError("Сессия истекла")

    user = await users.get_by_id(session.user_id)
    if (
        user is None
        or not user.is_active
        or user.email_verified is None
        or user.deleted_at is not None
    ):
        raise AuthenticationError("Не аутентифицирован")

    # BR-AUTH-011: extend no more than once per 24h
    should_extend = (
        session.last_used_at is None or (now - session.last_used_at) >= SESSION_EXTEND_INTERVAL
    )
    if should_extend:
        session.expires_at = now + SESSION_TTL
        session.last_used_at = now
        # commit happens in get_uow after the request

    conditions_groups = await user_permissions.get_grouped_by_permission(user.id)
    has_admin_access = await user_permissions.has_admin_access(user.id)
    children_count = await users.count_by_parent_id(user.id)
    return CurrentUser(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        parent_id=user.parent_id,
        name=user.name,
        permissions=conditions_groups,
        has_admin_access=has_admin_access,
        children_count=children_count,
        email_verified=user.email_verified is not None,
    )


def require_permission(code: str) -> Callable[..., Any]:
    async def checker(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> bool:
        if not user_has_permission(current_user, code):
            raise PermissionDeniedError(f"Недостаточно прав: {code}")
        return True

    return checker


def repos_for_sync_permissions(
    user_roles: UserRoleRepository = Depends(get_user_role_repo),
    role_permissions: RolePermissionRepository = Depends(get_role_permission_repo),
    user_direct_permissions: UserDirectPermissionRepository = Depends(
        get_user_direct_permission_repo
    ),
    user_permissions: UserPermissionRepository = Depends(get_user_permission_repo),
    permission_conditions: UserPermissionRepository = Depends(get_permission_condition_repo),
    user_organizations: UserPermissionRepository = Depends(get_user_organization_repo),
    permissions: PermissionRepository = Depends(get_permission_repo),
) -> dict[str, Any]:
    return {
        "user_roles": user_roles,
        "role_permissions": role_permissions,
        "user_direct_permissions": user_direct_permissions,
        "user_permissions": user_permissions,
        "permission_conditions": permission_conditions,
        "user_organizations": user_organizations,
        "permissions": permissions,
    }
