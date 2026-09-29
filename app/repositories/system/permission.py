"""
Session repo.
"""

from sqlalchemy import select

from app.dto.system.permission import PermissionOutput
from app.models import Permission
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
