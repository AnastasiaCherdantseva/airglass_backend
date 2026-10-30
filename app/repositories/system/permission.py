"""
Session repo.
"""

from uuid import UUID

from sqlalchemy import select

from app.dto.system.permission import PermissionOutput
from app.models import Permission
from app.models.system.permission_condition import PermissionCondition
from app.repositories.base import BaseIdRepository


class PermissionRepository(BaseIdRepository[Permission]):
    model = Permission

    async def get_by_code(self, code: str) -> PermissionOutput | None:
        """Find permission by code."""
        result = await self.db.execute(select(Permission).where(Permission.code == code))
        permission = result.scalar_one_or_none()
        if permission is None:
            return None
        return PermissionOutput(
            id=permission.id,
            code=permission.code,
            resource=permission.resource,
            action=permission.action,
            name=permission.name,
            description=permission.description,
            zone="admin" if permission.zone == "admin" else "public",
        )
    async def get_by_conditions(
        self, condition_ids: list[UUID]
    ) -> dict[PermissionOutput, list[UUID]]:
        if not condition_ids:
            return {}

        stmt = (
            select(Permission, PermissionCondition.id)
            .join(PermissionCondition, PermissionCondition.permission_id == Permission.id)
            .where(PermissionCondition.id.in_(condition_ids))
        )
        rows = (await self.db.execute(stmt)).all()

        grouped: dict[PermissionOutput, list[UUID]] = {}
        for permission, condition_id in rows:
            output = PermissionOutput(
                id=permission.id,
                name=permission.name,
                description=permission.description,
                code=permission.code,
                resource=permission.resource,
                action=permission.action,
                zone=permission.zone,
            )
            grouped.setdefault(output, []).append(condition_id)
        return grouped
