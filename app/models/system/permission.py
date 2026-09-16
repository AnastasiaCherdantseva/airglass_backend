import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Enum, Boolean, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models import (
        RolePermission,
        UserPermission,
        PermissionCondition,
    )


class PermissionResource(str, enum.Enum):
    """Ресурсы, к которым применяется право"""
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


class PermissionAction(str, enum.Enum):
    """Действия над ресурсом"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ARCHIVE = "archive"
    RESTORE = "restore"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    ASSIGN = "assign"
    MANAGE = "manage"


class PermissionScope(str, enum.Enum):
    """Область действия права"""
    ALL = "all"
    OWN = "own"
    DEPARTMENT = "department"
    ASSIGNED = "assigned"
    SPECIFIC = "specific"


class Permission(Base, TimestampMixin):
    """
    Атомарное право доступа.
    """
    __tablename__ = "permissions"
    __table_args__ = (
        Index("ix_permission_resource_action", "resource", "action"),
        Index("ix_permission_code", "code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    code: Mapped[str] = mapped_column(String(150), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    resource: Mapped[PermissionResource] = mapped_column(Enum(PermissionResource))
    action: Mapped[PermissionAction] = mapped_column(Enum(PermissionAction))
    scope: Mapped[PermissionScope] = mapped_column(
        Enum(PermissionScope),
        default=PermissionScope.ALL,
        server_default=text("'ALL'"),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
    )

    # Связи
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )
    user_permissions: Mapped[list["UserPermission"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )
    conditions: Mapped[list["PermissionCondition"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )

    @staticmethod
    def generate_code(
        resource: PermissionResource,
        action: PermissionAction,
        scope: PermissionScope,
    ) -> str:
        """Генерирует код права: users.create.all"""
        return f"{resource.value}.{action.value}.{scope.value}"