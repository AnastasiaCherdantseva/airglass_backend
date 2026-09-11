import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Связи
    user_roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_permissions = relationship(
        "UserPermission",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    audit_logs = relationship("AuditLog", back_populates="user")
    created_templates = relationship("Template", foreign_keys="Template.created_by")
    uploaded_media = relationship("MediaFile", foreign_keys="MediaFile.created_by")

    # ========================================
    # МЕТОДЫ ПРОВЕРКИ ПРАВ
    # ========================================

    def has_permission(
        self,
        resource: str,
        action: str,
        scope: str = "all",
        target=None,
    ) -> bool:
        """
        Проверяет, есть ли у пользователя право.
        
        Args:
            resource: 'users', 'products', 'templates'...
            action: 'create', 'read', 'update', 'delete'...
            scope: 'all', 'own'...
            target: объект, над которым выполняется действие (для проверки условий)
        
        Returns:
            True, если право есть.
        """
        # 1. Права через роли
        for user_role in self.user_roles:
            for role_permission in user_role.role.role_permissions:
                permission = role_permission.permission
                if self._matches(permission, resource, action, scope):
                    if self._check_conditions(permission, target):
                        return True

        # 2. Индивидуальные права пользователя (приоритет выше)
        for user_permission in self.user_permissions:
            permission = user_permission.permission
            if self._matches(permission, resource, action, scope):
                if self._check_conditions(permission, target):
                    return True

        return False

    def _matches(
        self,
        permission,
        resource: str,
        action: str,
        scope: str,
    ) -> bool:
        """Проверяет, соответствует ли право запросу."""
        # Админ может всё
        if permission.action.value == "manage":
            return permission.resource.value == resource

        return (
            permission.resource.value == resource
            and permission.action.value == action
            and permission.scope.value in (scope, "all")
        )

    def _check_conditions(self, permission, target) -> bool:
        """Проверяет условия права (например, только для роли X)."""
        if not permission.conditions:
            return True

        for condition in permission.conditions:
            if condition.type == "role":
                # Только для пользователей с ролью X
                if not hasattr(target, "user_roles"):
                    return False
                target_role_ids = [ur.role_id for ur in target.user_roles]
                if condition.value not in [str(r) for r in target_role_ids]:
                    return False
            elif condition.type == "category":
                # Только для товаров из категории X
                if not hasattr(target, "category_id"):
                    return False
                if str(target.category_id) != condition.value:
                    return False
            elif condition.type == "creator":
                # Только созданные текущим пользователем
                if not hasattr(target, "created_by"):
                    return False
                if target.created_by != self.id:
                    return False

        return True

    def has_role(self, role_code: str) -> bool:
        """Проверяет, есть ли у пользователя роль с кодом."""
        return any(ur.role.code == role_code for ur in self.user_roles)

    def has_any_role(self, role_codes: list[str]) -> bool:
        """Проверяет, есть ли у пользователя хотя бы одна из ролей."""
        return any(ur.role.code in role_codes for ur in self.user_roles)