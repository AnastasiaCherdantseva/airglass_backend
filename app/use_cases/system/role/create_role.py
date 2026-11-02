"""
UseCase: get roles available to the current user.

UseCase: получить роли, доступные текущему пользователю.
"""

import logging
from dataclasses import replace
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, PermissionDeniedError
from app.dto import (
    CurrentUser,
    RoleWithPermissionsOutput,
)
from app.dto.system.permission_condition import PermissionConditionAllData
from app.dto.system.role import RoleCreate
from app.dto.system.user_permission import GroupedPermission
from app.models.system.permission_condition import ConditionType
from app.repositories.protocols.system import (
    RolePermissionRepositoryProtocol,
    RoleRepositoryProtocol,
)
from app.repositories.protocols.system.permission_condition import (
    PermissionConditionWriteRepositoryProtocol,
)
from app.repositories.protocols.system.user_direct_permission import (
    UserDirectPermissionWriteRepositoryProtocol,
)
from app.repositories.protocols.system.user_permission import UserPermissionWriteRepositoryProtocol
from app.services.condition_package import build_full_conditions_package
from app.services.grant_conditions import grant_conditions_to_user

logger = logging.getLogger(__name__)

NEW_ROLE_CONDITION_CODES: dict[str, ConditionType] = {
    "USERS.CREATE": ConditionType.ROLE,
}


async def create_role(
    actor: CurrentUser,
    data: RoleCreate,
    *,
    roles: RoleRepositoryProtocol,
    role_permissions: RolePermissionRepositoryProtocol,
    permission_conditions: PermissionConditionWriteRepositoryProtocol,
    user_direct_permissions: UserDirectPermissionWriteRepositoryProtocol,
    user_permissions: UserPermissionWriteRepositoryProtocol,
) -> RoleWithPermissionsOutput:

    # 1. Проверить кому присваивается роль
    if actor.id != data.owner_id:
        logger.info(
            "Create role error: actor with id (%s) try to create role with another owner id (%s)",
            actor.id,
            data.owner_id,
        )
        raise PermissionDeniedError("Вы не можете создавать роли не пренадлежащие вам.")

    # 3. Полный пакет прав, если фронт прислал права которые должны идти только вместе без своих пар
    full_ids = build_full_conditions_package(
        actor=actor,
        requested_condition_ids=set(data.conditions),
    )

    # 4. нормализуем данные
    normalised_name = data.name.strip().capitalize()
    normalised_data = replace(data, name=normalised_name, conditions=list(full_ids))

    try:
        # 5. Пытаемся создать новую роль
        new_role = await roles.create(normalised_data)

        # 6. Выдаем ем права
        conditions_for_role_count = await role_permissions.add_links_for_role(
            new_role.id, normalised_data.conditions
        )
    except IntegrityError as exc:
        constraint_name = (
            getattr(exc.orig, "constraint_name", None)
            or getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
            or getattr(getattr(exc.orig, "__cause__", None), "constraint_name", "")
        )
        if constraint_name == "uq_role_owner_name":
            logger.info(
                "Create role error: actor with id (%s) already has role with name %s",
                normalised_data.owner_id,
                normalised_data.name,
            )
            raise ConflictError("У вас уже существует роль с таким именем.") from exc
        logger.exception("Unexpected IntegrityError in create_organization")
        raise ConflictError("Не удалось создать роль.") from exc

    # 7. Проверяем что все права выдались
    if conditions_for_role_count < len(normalised_data.conditions):
        logger.info(
            "Create role error: added %s relationships for role&conds, but It was expected %s.",
            conditions_for_role_count,
            len(normalised_data.conditions),
        )
        raise ConflictError("Не удалось добавить все права к роли.")

    # 8. Создать новые условия для управления ролью
    #    (USERS.CREATE/ROLE с role_id=new_role.id)
    #    — только если USERS.CREATE был среди запрошенных условий.

    new_conditions: list[UUID] = []
    for code, cond_type in NEW_ROLE_CONDITION_CODES.items():
        permission = next((p for p in actor.permissions if p.code == code), None)
        if permission is None:
            logger.warning(
                "Create role warning: permission %s not found (actor=%s, role=%s) — skipped",
                code,
                actor.id,
                new_role.id,
            )
            continue
        new_data = PermissionConditionAllData(
            permission_id=permission.id,
            type=cond_type,
            role_id=new_role.id,
            is_active=True,
        )
        new_cond = await permission_conditions.create(new_data)
        new_conditions.append(new_cond.id)

    await grant_conditions_to_user(
        actor.id,
        new_conditions,
        user_direct_permissions=user_direct_permissions,
        user_permissions=user_permissions,
    )

    # 8. Возвращаем данные
    condition_ids_set = set(normalised_data.conditions)
    grouped = []
    for src in actor.permissions:
        filtered = [c for c in src.conditions if c.id in condition_ids_set]
        if filtered:
            grouped.append(
                GroupedPermission(
                    id=src.id,
                    code=src.code,
                    name=src.name,
                    conditions=filtered,
                )
            )

    return RoleWithPermissionsOutput(
        name=new_role.name,
        owner_id=new_role.owner_id,
        description=new_role.description,
        is_system=new_role.is_system,
        is_active=new_role.is_active,
        id=new_role.id,
        created_at=new_role.created_at,
        updated_at=new_role.updated_at,
        permissions=grouped,
    )
