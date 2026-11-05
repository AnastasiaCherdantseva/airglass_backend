"""
UseCase: получить пользователя по id.
"""

import logging
from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from app.core.security import hash_password
from app.dto import CurrentUser, UserCreate, UserCreateFull, UserRoleLink, UserWithRolesOutput
from app.dto.system.permission_condition import PermissionConditionAllOutPut
from app.models.system.permission_condition import (
    ConditionType,
    # PermissionEffect
)
from app.repositories.protocols.system import (
    UserOrganizationRepositoryProtocol,
    UserPermissionWriteRepositoryProtocol,
    UserRoleRepositoryProtocol,
    OrganizationReadRepositoryProtocol,
    RoleReadRepositoryProtocol,
    RolePermissionReadRepositoryProtocol,
    UserRepositoryProtocol,
    UserDirectPermissionRepositoryProtocol)
from app.services.sync_user_permissions import sync_user_permissions

logger = logging.getLogger(__name__)


async def create_user(
    actor: CurrentUser,
    data: UserCreate,
    *,
    users: UserRepositoryProtocol,
    roles: RoleReadRepositoryProtocol,
    user_role: UserRoleRepositoryProtocol,
    user_direct_permissions: UserDirectPermissionRepositoryProtocol,
    deps_for_sync: dict[str, Any],
) -> UserWithRolesOutput:
    """
    Create a user, validate requested roles and organizations, and sync permissions.

    Args:
        actor: User performing the operation.
        data: New user's data, roles, and optional organizations.
        users: Repository for user operations.
        roles: Repository for reading roles.
        user_role: Repository for user-role links.
        role_permissions: Repository for role permission conditions.
        user_direct_permissions: Repository for direct user permissions.
        user_permissions: Repository for effective user permissions.
        organizations: Repository for reading organizations.
        user_organizations: Repository for user-organization links.

    Raises:
        PermissionDeniedError: Actor lacks required permissions or owns none of the requested organizations.
        ConflictError: Email already exists.
        NotFoundError: A requested role or organization does not exist.
        ValidationError: No roles supplied or a requested role is inactive.

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
        if
        # condition.effect == PermissionEffect.ALLOW and
        condition.type == ConditionType.ROLE and condition.is_active
    ]

    if not data.role_ids or len(data.role_ids) == 0:
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

    if data.additional_condition_ids:
        actor_conditions: dict[UUID, tuple[str, PermissionConditionAllOutPut]] = {
            cond.id: (perm.code, cond)
            for perm in actor.permissions
            for cond in perm.conditions
        }
        foreign = data.additional_condition_ids - actor_conditions.keys()
        if foreign:
            logger.info(
                "User create failed: User(%s) has not conditions(%s) to share with new user",
                actor.id,
                foreign,
            )
            raise PermissionDeniedError(
                f"Пользователь {actor.id} не может назначать передаваемые права: {len(foreign)} шт."
            )
        
    password_hash = hash_password(data.password)

    full_data = UserCreateFull(
        email=data.email,
        name=data.name,
        parent_id=actor.id,
        password_hash=password_hash,
        is_active=False,  # BR-USERS-003.
    )
    user = await users.create(full_data)

    await user_direct_permissions.add_links(user.id,data.additional_condition_ids)

    role_links = [UserRoleLink(user_id=user.id, role_id=role_id) for role_id in data.role_ids]
    await user_role.add_links(role_links)

    await sync_user_permissions(user.id, **deps_for_sync)
    children_count = await users.count_by_parent_id(user.id)
    return UserWithRolesOutput(
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        id=user.id,
        parent_id=user.parent_id,
        role_ids=data.role_ids,
        children_count=children_count,
        email_verified=user.email_verified,
    )
