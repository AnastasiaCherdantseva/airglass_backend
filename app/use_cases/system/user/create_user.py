"""
UseCase: получить пользователя по id.
"""

import logging

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from app.core.security import hash_password
from app.dto import CurrentUser, UserCreate, UserCreateFull, UserRoleLink, UserWithRolesOutput
from app.models.system.permission_condition import ConditionType, PermissionEffect
from app.repositories.protocols.system.organization import OrganizationReadRepositoryProtocol
from app.repositories.protocols.system.role import RoleReadRepositoryProtocol
from app.repositories.protocols.system.role_permission import RolePermissionReadRepositoryProtocol
from app.repositories.protocols.system.user import UserRepositoryProtocol
from app.repositories.protocols.system.user_direct_permission import (
    UserDirectPermissionReadRepositoryProtocol,
)
from app.repositories.protocols.system.user_organization import UserOrganizationRepositoryProtocol
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
    organizations: OrganizationReadRepositoryProtocol,
    user_organizations: UserOrganizationRepositoryProtocol,
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

    if data.organization_ids:
        found_orgs = await organizations.get_by_ids(data.organization_ids)
        found_ids = {o.id for o in found_orgs}
        missing_ids = [oid for oid in data.organization_ids if oid not in found_ids]

        if missing_ids:
            logger.info(
                "User create failed: Organizations not found (ids: %s)",
                missing_ids,
            )
            missing_ids_str = ", ".join(str(item) for item in missing_ids)
            raise NotFoundError(f"Не найдены организации: {missing_ids_str}")

        foreign_ids = [
            organization.id for organization in found_orgs if organization.owner_id != actor.id
        ]
        if foreign_ids:
            logger.info(
                "User create failed: Actor(%s) does not own organizations (ids: %s)",
                actor.id,
                foreign_ids,
            )
            foreign_ids_str = ", ".join(str(item) for item in foreign_ids)
            raise PermissionDeniedError(
                f"Пользователь не является владельцем организаций: {foreign_ids_str}"
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

    role_links = [UserRoleLink(user_id=user.id, role_id=role_id) for role_id in data.role_ids]
    await user_role.add_links(role_links)

    await user_organizations.add_links_to_user(user.id, data.organization_ids)
    await sync_user_permissions(
        user.id,
        user_roles=user_role,
        role_permissions=role_permissions,
        user_direct_permissions=user_direct_permissions,
        user_permissions=user_permissions,
    )
    children_count = await users.count_by_parent_id(user.id)
    return UserWithRolesOutput(
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        id=user.id,
        parent_id=user.parent_id,
        role_ids=data.role_ids,
        children_count=children_count,
    )
