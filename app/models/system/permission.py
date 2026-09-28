"""
Permission — atomic access right.
Immutable reference. No is_active (moved to PermissionCondition).
No scope (expressed via PermissionCondition.type).
"""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Computed, Enum, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.system.permission_condition import PermissionCondition


class PermissionResource(enum.StrEnum):
    """Resources the permission applies to."""

    USERS = "users"
    ROLES = "roles"
    PRODUCTS = "products"
    CATEGORIES = "categories"
    TEMPLATES = "templates"
    PROJECTS = "projects"
    CUSTOMERS = "customers"
    SUPPLIERS = "suppliers"
    MEDIA = "media"
    CALCULATOR = "calculator"
    SETTINGS = "settings"
    AUDIT_LOG = "audit_log"


class PermissionAction(enum.StrEnum):
    """Actions on a resource."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ARCHIVE = "archive"  # includes RESTORE BR-ACCESS-038
    EXPORT = "export"
    IMPORT = "import"


class PermissionZone(enum.StrEnum):
    """Zone where the permission applies."""

    PUBLIC = "public"
    ADMIN = "admin"


class Permission(Base):
    """Atomic access right. Immutable reference."""

    __tablename__ = "permissions"
    __table_args__ = (
        Index("ix_permission_resource_action", "resource", "action"),
        CheckConstraint(
            """
            NOT (
                (resource = 'USERS'      AND action = 'ARCHIVE') OR
                (resource = 'PROJECTS'   AND action IN ('IMPORT', 'EXPORT')) OR
                (resource = 'CUSTOMERS'  AND action = 'ARCHIVE') OR
                (resource = 'MEDIA'      AND action IN ('ARCHIVE', 'EXPORT', 'IMPORT')) OR
                (resource = 'CALCULATOR' AND action IN ('ARCHIVE', 'IMPORT')) OR
                (resource = 'SETTINGS'   AND action IN ('CREATE', 'DELETE', 'ARCHIVE', 'EXPORT', 'IMPORT')) OR
                (resource = 'AUDIT_LOG'  AND action IN ('CREATE', 'UPDATE', 'DELETE', 'ARCHIVE', 'IMPORT'))
            )
            """,
            name="ck_permission_forbidden_combinations",
        ),
        CheckConstraint(
            """
        (resource IN ('USERS', 'ROLES', 'PROJECTS', 'CUSTOMERS', 'CALCULATOR', 'MEDIA')
            AND zone = 'PUBLIC') OR
        (resource IN ('PRODUCTS', 'CATEGORIES', 'TEMPLATES', 'SUPPLIERS', 'SETTINGS', 'AUDIT_LOG')
            AND zone = 'ADMIN')
        """,
            name="ck_permission_zone_by_resource",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    # BR-ACCESS-006
    code: Mapped[str] = mapped_column(
        String(150), Computed("permission_code(resource, action)", persisted=True), unique=True
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    resource: Mapped[PermissionResource] = mapped_column(Enum(PermissionResource), nullable=False)
    action: Mapped[PermissionAction] = mapped_column(Enum(PermissionAction), nullable=False)

    is_system: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    zone: Mapped[PermissionZone] = mapped_column(
        Enum(PermissionZone, name="permission_zone"),
        nullable=False,
    )
    # BR-ACCESS-039
    conditions: Mapped[list["PermissionCondition"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )
