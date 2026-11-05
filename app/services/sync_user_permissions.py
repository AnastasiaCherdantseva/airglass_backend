"""
UseCase: синхронизация user_permissions для пользователя.
"""

from dataclasses import dataclass
import logging
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.system.permission_condition import ConditionType
from app.repositories.protocols.system import (
    RolePermissionReadRepositoryProtocol,
    UserDirectPermissionReadRepositoryProtocol,
    UserPermissionWriteRepositoryProtocol,
    UserRoleReadRepositoryProtocol,
)
from app.repositories.protocols.system.permission import PermissionReadRepositoryProtocol
from app.repositories.protocols.system.permission_condition import PermissionConditionReadRepositoryProtocol
from app.repositories.protocols.system.user_organization import UserOrganizationRepositoryProtocol

logger = logging.getLogger(__name__)

# @dataclass(frozen=True)
# class LinkSyncRule:
#     permission_code: str
#     condition_type: ConditionType
#     source_field: str
    
# LINK_SYNC_RULES: list[LinkSyncRule] = [
#     LinkSyncRule(
#         permission_code="ORGANIZATIONS.READ",
#         condition_type=ConditionType.ORGANIZATION,
#         source_field="organization_id",
#     ),
# ]


async def sync_user_organization_links(
    user_id: UUID,
    condition_ids: list[UUID],
    *,
    permission_conditions: PermissionConditionReadRepositoryProtocol,
    user_organizations: UserOrganizationRepositoryProtocol,
    permissions: PermissionReadRepositoryProtocol,
) -> int:
    """
    Добавить недостающие связи UserOrganization для условий
    ORGANIZATIONS.READ.
    
    Для каждого условия с ``permission_code == "ORGANIZATIONS.READ"`` и
    ``type == ORGANIZATION`` убедиться, что у пользователя есть связь
    ``UserOrganization`` с ``organization_id``. Существующие связи не
    трогаются.

    Args:
        user_id: Целевой пользователь.
        condition_ids: ID условий (эффективные права).
        permission_conditions: Репозиторий чтения условий.
        user_organizations: Репозиторий связей пользователь-организация.

    Returns:
        Количество созданных связей.
    """
    if not condition_ids:
        return 0

    organizations_read = await permissions.get_by_code("ORGANIZATIONS.READ")
    if organizations_read is None:
        return 0

    conditions = await permission_conditions.get_by_ids(condition_ids)

    required_organization_ids: set[UUID] = {
        cond.organization_id
        for cond in conditions
        if cond.type == ConditionType.ORGANIZATION
        and cond.organization_id is not None
        and cond.permission_id == organizations_read.id
    }

    if not required_organization_ids:
        return 0

    existing = set(
        await user_organizations.get_organization_ids_by_user_id(user_id)
    )
    missing = required_organization_ids - existing
    for organization_id in missing:
        await user_organizations.add_link(user_id, organization_id)

    if missing:
        logger.info(
            "sync_user_organization_links: added %d links (user_id=%s)",
            len(missing),
            user_id,
        )
    return len(missing)

async def sync_user_permissions(
    user_id: UUID,
    *,
    user_roles: UserRoleReadRepositoryProtocol,
    role_permissions: RolePermissionReadRepositoryProtocol,
    user_direct_permissions: UserDirectPermissionReadRepositoryProtocol,
    user_permissions: UserPermissionWriteRepositoryProtocol,
    permission_conditions: PermissionConditionReadRepositoryProtocol,
    user_organizations: UserOrganizationRepositoryProtocol,
    permissions: PermissionReadRepositoryProtocol,
) -> None:
    """
    Собрать все condition_id пользователя и записать в user_permissions.

    Шаги:
        1. Активные роли пользователя (BR-ROLE-023).
        2. Conditions из этих ролей.
        3. Direct conditions пользователя.
        4. Объединение через set() — дедупликация.
        5.Добавить прямые связи с сущностями из прав
        6. replace_for_user.

    См. BR-ACCESS-028, ADR-ACCESS-018.
    """
    # 1. Активные роли
    roles = await user_roles.get_roles_by_user_id(user_id)
    if not roles:
        logger.info("Sync user permissions failed: roles for user not found(user: %s)", user_id)
        raise NotFoundError("Не удалось найти роли пользователя.")

    # 2. Conditions из ролей
    role_ids = [r.id for r in roles]
    conditions_from_roles: list[UUID] = await role_permissions.get_condition_ids_by_role_ids(
        role_ids
    )

    # 3. Direct conditions
    conditions_from_direct = await user_direct_permissions.get_condition_ids_by_user_id(user_id)

    # 4. Объединение — дедупликация
    all_conditions = list(set(conditions_from_roles + conditions_from_direct))


    # 5. Замена
    await user_permissions.replace_for_user(user_id, all_conditions)
    await sync_user_organization_links(
        user_id,
        all_conditions,
        permission_conditions=permission_conditions,
        user_organizations=user_organizations,
        permissions=permissions,
    )

    logger.info(
        "Synced user_permissions (user_id=%s, roles=%d, conditions=%d)",
        user_id,
        len(roles),
        len(all_conditions),
    )
