"""
UseCase: получить пользователя по id.
"""

import logging

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from app.core.security import hash_password
from app.dto import CurrentUser, UserCreate, UserCreateFull, UserRoleLink, UserWithRolesOutput
from app.models.system.permission_condition import ConditionType, PermissionEffect
from app.repositories.protocols.system.role import RoleReadRepositoryProtocol
from app.repositories.protocols.system.role_permission import RolePermissionReadRepositoryProtocol
from app.repositories.protocols.system.user import UserRepositoryProtocol
from app.repositories.protocols.system.user_direct_permission import (
    UserDirectPermissionReadRepositoryProtocol,
)
from app.repositories.protocols.system.user_permission import UserPermissionWriteRepositoryProtocol
from app.repositories.protocols.system.user_role import UserRoleRepositoryProtocol
from app.services.sync_user_permissions import sync_user_permissions

logger = logging.getLogger(__name__)


async def create_user(
    actor: CurrentUser,
    data: UserCreate,
    *,
    users: UserRepositoryProtocol,
    roles: RoleReadRepositoryProtocol,
    user_role: UserRoleRepositoryProtocol,
    role_permissions: RolePermissionReadRepositoryProtocol,
    user_direct_permissions: UserDirectPermissionReadRepositoryProtocol,
    user_permissions: UserPermissionWriteRepositoryProtocol,
) -> UserWithRolesOutput:
    """
    Create a user, assign roles, and materialize permissions.

    Steps:
        1. Check actor has `users.create` with `type=ROLE` for every
        requested role (BR-ROLE-022).
        2. Check email uniqueness (BR-USERS-002).
        3. Hash password (ADR-USER-001).
        4. Create User with parent_id = actor.id.
        5. Link roles via UserRole.
        6. Sync user_permissions.

    Raises:
        PermissionDeniedError: actor lacks permission for a role.
        ConflictError: email already exists.
    """
    conditions = next(
        (
            permission.conditions
            for permission in actor.permissions
            if permission.code == "USERS.CREATE"
        ),
        None,
    )
    if conditions is None:
        logger.info("User create failed: no USERS.CREATE (actor=%s)", actor.id)
        raise PermissionDeniedError("Нет права на создание пользователя")

    condition_roles = [
        condition.role_id
        for condition in conditions
        if condition.effect == PermissionEffect.ALLOW
        and condition.type == ConditionType.ROLE
        and condition.is_active
    ]

    if not data.role_ids:
        logger.info(
            "User create failed: The new user must have at least one role",
        )
        raise ValidationError("У нового пользователя должна быть хотя бы одна роль.")
    current_roles = await roles.get_by_ids(data.role_ids)

    if len(current_roles) != len(data.role_ids):
        logger.info("User create failed: One of the current role not found(ids: %s)", data.role_ids)
        raise NotFoundError("Не удалось найти одну из ролей.")
    for r in current_roles:
        if not r.is_active:
            logger.info("User create failed: Role with id %s is not active", data.role_ids)
            raise ValidationError(
                f"Нельзя создать пользователя с неактивной ролью ({r.name}). Активируйте роль, прежде чем создать пользователя."
            )
    allowed = set(condition_roles)

    for role_id in data.role_ids:
        if role_id not in allowed:
            logger.info(
                "User create failed: User(%s) has not permissions for create role with id %s",
                actor.id,
                role_id,
            )
            raise PermissionDeniedError(
                f"Пользователь {actor.id} не может создавать пользователя с ролью {role_id}"
            )

    is_unique_email = await users.get_by_email(data.email) is None
    if not is_unique_email:
        logger.info(
            "User create failed: User with email '%s' already exist",
            data.email,
        )
        raise ConflictError(f"Пользователь с почтой {data.email} уже существует.")

    password_hash = hash_password(data.password)

    full_data = UserCreateFull(
        email=data.email,
        name=data.name,
        parent_id=actor.id,
        password_hash=password_hash,
        is_active=False,  # BR-USERS-003.
    )
    user = await users.create(full_data)

    role_links = [UserRoleLink(user_id=user.id, role_id=role_id) for role_id in data.role_ids]
    await user_role.add_links(role_links)

    await sync_user_permissions(
        user.id,
        user_roles=user_role,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct_permissions,
        user_permissions=user_permissions,
    )

    return UserWithRolesOutput(
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        id=user.id,
        parent_id=user.parent_id,
        role_ids=data.role_ids,
    )
