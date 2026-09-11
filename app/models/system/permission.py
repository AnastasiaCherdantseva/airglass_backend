import uuid
import enum
from sqlalchemy import Column, String, Text, Enum, Boolean, Index,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


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
    MANAGE = "manage"  # все действия


class PermissionScope(str, enum.Enum):
    """Область действия права"""
    ALL = "all"              # все объекты
    OWN = "own"              # только свои
    DEPARTMENT = "department"  # только своего отдела
    ASSIGNED = "assigned"    # только назначенные
    SPECIFIC = "specific"    # только конкретные (через отдельную таблицу)


class Permission(Base, TimestampMixin):
    """
    Атомарное право доступа.
    
    Примеры:
    - users.create.all       — создавать любых пользователей
    - users.delete.own       — удалять только своих пользователей
    - products.update.all    — редактировать любые товары
    - templates.delete.own   — удалять только свои шаблоны
    """
    __tablename__ = "permissions"
    __table_args__ = (
        Index("ix_permission_resource_action", "resource", "action"),
        Index("ix_permission_code", "code"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(150), unique=True, nullable=False)  # users.create.all
    name = Column(String(255), nullable=False)               # Создание пользователей
    description = Column(Text, nullable=True)

    resource = Column(Enum(PermissionResource), nullable=False)
    action = Column(Enum(PermissionAction), nullable=False)
    scope = Column(Enum(PermissionScope), nullable=False, default=PermissionScope.ALL)

    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # системное право (нельзя удалить)

    # Связи
    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )
    user_permissions = relationship(
        "UserPermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )
    conditions = relationship(
        "PermissionCondition",
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


class PermissionConditionType(str, enum.Enum):
    """Тип условия для права"""
    ROLE = "role"                    # только пользователи с ролью X
    CATEGORY = "category"            # только товары из категории X
    CREATOR = "creator"              # только созданные текущим пользователем
    CUSTOM = "custom"                # кастомное условие


class PermissionCondition(Base):
    """
    Условие для права — уточняет, к каким объектам применяется право.
    
    Примеры:
    - users.delete.role_manager — удалять только пользователей с ролью "менеджер"
    - products.update.category_glass — редактировать только товары из категории "Стекло"
    - templates.delete.own — удалять только свои шаблоны
    """
    __tablename__ = "permission_conditions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(Enum(PermissionConditionType), nullable=False)
    value = Column(String(255), nullable=False)  # ID роли, ID категории и т.д.
    description = Column(Text, nullable=True)

    # Связи
    permission = relationship("Permission", back_populates="conditions")