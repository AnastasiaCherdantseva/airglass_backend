"""
UserDirectPermission — manual override (source).
References conditions with ALLOW or DENY effect.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.system.permission_condition import PermissionCondition
    from app.models.system.user import User


class UserDirectPermission(Base):
    """Manual override. References ALLOW or DENY conditions."""

    __tablename__ = "user_direct_permissions"
    __table_args__ = (Index("ix_user_direct_permission_user_id", "user_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    condition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permission_conditions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(back_populates="user_direct_permissions")
    condition: Mapped["PermissionCondition"] = relationship(
        back_populates="user_direct_permissions"
    )
