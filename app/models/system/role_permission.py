"""
RolePermission — link between role and permission condition.
Only effect = ALLOW is allowed (BR-ACCESS-022).
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.system.permission_condition import PermissionCondition
    from app.models.system.role import Role


class RolePermission(Base):
    """Link between role and permission condition. ALLOW only."""

    __tablename__ = "role_permissions"
    __table_args__ = (Index("ix_role_permission_role_id", "role_id"),)

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    condition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permission_conditions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped["Role"] = relationship(back_populates="role_permissions")
    condition: Mapped["PermissionCondition"] = relationship(back_populates="role_permissions")
