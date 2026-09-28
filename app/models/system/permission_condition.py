"""
PermissionCondition — variant of a permission.
Immutable: created or deleted, never updated.
is_active allows soft-disable without losing links.
"""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.catalog import Category
    from app.models.media import MediaType
    from app.models.system.permission import Permission
    from app.models.system.role import Role
    from app.models.system.role_permission import RolePermission
    from app.models.system.user_direct_permission import UserDirectPermission
    from app.models.system.user_permission import UserPermission


class ConditionType(enum.StrEnum):
    """Type of a permission condition."""

    ALL = "all"
    CATEGORY = "category"
    ROLE = "role"
    CREATOR = "creator"
    SUBTREE = "subtree"
    MEDIA = "media"


class PermissionEffect(enum.StrEnum):
    """Effect of a permission condition."""

    ALLOW = "allow"
    DENY = "deny"


class PermissionCondition(Base):
    """Variant of a permission. Immutable. Soft-disable via is_active."""

    __tablename__ = "permission_conditions"
    __table_args__ = (
        UniqueConstraint(
            # BR-ACCESS-004.BR-ACCESS-009
            "permission_id",
            "type",
            "effect",
            "category_id",
            "role_id",
            "media_type_id",
            name="uq_permission_condition",
        ),
        # ADR-ACCESS-011
        CheckConstraint(
            """
            (type = 'ALL'      AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL) OR
            (type = 'CATEGORY' AND category_id IS NOT NULL AND role_id IS NULL AND media_type_id IS NULL) OR
            (type = 'ROLE'     AND role_id IS NOT NULL AND category_id IS NULL AND media_type_id IS NULL) OR
            (type = 'CREATOR'  AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL) OR
            (type = 'SUBTREE'  AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL) OR
            (type = 'MEDIA'    AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NOT NULL)
            """,
            name="ck_permission_condition_type",
        ),
        Index("ix_permission_condition_permission_id", "permission_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[ConditionType] = mapped_column(Enum(ConditionType), nullable=False)
    effect: Mapped[PermissionEffect] = mapped_column(
        Enum(PermissionEffect, name="permission_effect"),
        server_default=text("'ALLOW'"),
        nullable=False,
    )

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
    )
    media_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "media_types.id", ondelete="CASCADE", name="fk_permission_condition_media_type_id"
        ),
        nullable=True,
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=True,
    )
    #  ADR-ACCESS-004.
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("true"), nullable=False
    )

    # ///////////////////////////

    permission: Mapped["Permission"] = relationship(back_populates="conditions")
    # ADR-ACCESS-011
    category: Mapped["Category | None"] = relationship(
        back_populates="conditions",
    )
    media_type: Mapped["MediaType | None"] = relationship(back_populates="conditions")
    # ADR-ACCESS-011
    role: Mapped["Role | None"] = relationship(back_populates="conditions")

    # BR-ACCESS-029
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="condition",
        cascade="all, delete-orphan",
    )
    # BR-ACCESS-029
    user_direct_permissions: Mapped[list["UserDirectPermission"]] = relationship(
        back_populates="condition",
        cascade="all, delete-orphan",
    )
    # BR-ACCESS-029
    user_permissions: Mapped[list["UserPermission"]] = relationship(
        back_populates="condition",
        cascade="all, delete-orphan",
    )
