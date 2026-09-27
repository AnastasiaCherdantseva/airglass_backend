"""
Permission — atomic access right.
Immutable reference. No is_active (moved to PermissionCondition).
No scope (expressed via PermissionCondition.type).
"""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Computed, Enum, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.system.permission_condition import PermissionCondition


# BR-ACCESS-035. BR-ACCESS-036. ADR-ACCESS-014.
class PermissionResource(enum.StrEnum):
    """Resources the permission applies to."""

    USERS = "users"
    ROLES = "roles"
    PRODUCTS = "products"
    CATEGORIES = "categories"
    TEMPLATES = "templates"
    QUOTES = "quotes"
    PROJECTS = "projects"
    CUSTOMERS = "customers"
    SUPPLIERS = "suppliers"
    MEDIA = "media"
    CALCULATOR = "calculator"
    SETTINGS = "settings"
    AUDIT_LOG = "audit_log"


# BR-ACCESS-035. BR-ACCESS-037. ADR-ACCESS-014.
class PermissionAction(enum.StrEnum):
    """Actions on a resource."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ARCHIVE = "archive"  # includes RESTORE BR-ACCESS-038
    EXPORT = "export"
    IMPORT = "import"


class Permission(Base):
    """Atomic access right. Immutable reference."""

    __tablename__ = "permissions"
    __table_args__ = (Index("ix_permission_resource_action", "resource", "action"),)

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
    # BR-ACCESS-039
    conditions: Mapped[list["PermissionCondition"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )
