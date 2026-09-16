import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models import (
        UserRole,
        UserPermission,
        UserMedia,
        AuditLog,
        Template,
        MediaFile,
        Permission,
    )


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
    )

    # Связи
    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_permissions: Mapped[list["UserPermission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_media: Mapped[list["UserMedia"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")
    created_templates: Mapped[list["Template"]] = relationship(
        foreign_keys="Template.created_by",
    )
    uploaded_media: Mapped[list["MediaFile"]] = relationship(
        foreign_keys="MediaFile.created_by",
    )

    # ========================================
    # МЕТОДЫ ПРОВЕРКИ ПРАВ
    # ========================================

    def has_permission(
        self,
        resource: str,
        action: str,
        scope: str = "all",
        target: Any = None,
    ) -> bool:
        """
        Проверяет, есть ли у пользователя право.
        """
        # 1. Права через роли
        for user_role in self.user_roles:
            for role_permission in user_role.role.role_permissions:
                permission = role_permission.permission
                if self._matches(permission, resource, action, scope):
                    if self._check_conditions(permission, target):
                        return True

        # 2. Индивидуальные права пользователя
        for user_permission in self.user_permissions:
            permission = user_permission.permission
            if self._matches(permission, resource, action, scope):
                if self._check_conditions(permission, target):
                    return True

        return False

    def _matches(
        self,
        permission: "Permission",
        resource: str,
        action: str,
        scope: str,
    ) -> bool:
        """Проверяет, соответствует ли право запросу."""
        if permission.action.value == "manage":
            return permission.resource.value == resource

        return (
            permission.resource.value == resource
            and permission.action.value == action
            and permission.scope.value in (scope, "all")
        )

    def _check_conditions(self, permission: "Permission", target: Any) -> bool:
        """Проверяет условия права."""
        if not permission.conditions:
            return True

        for condition in permission.conditions:
            if condition.type == "role":
                if not hasattr(target, "user_roles"):
                    return False
                target_role_ids = [ur.role_id for ur in target.user_roles]
                if condition.value not in [str(r) for r in target_role_ids]:
                    return False
            elif condition.type == "category":
                if not hasattr(target, "category_id"):
                    return False
                if str(target.category_id) != condition.value:
                    return False
            elif condition.type == "creator":
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

    @property
    def logo(self) -> Any:
        """Лого компании (primary)."""
        for media in self.user_media:
            if media.media_type.code == "COMPANY_LOGO":
                return media.media_file
        return None

    @property
    def avatar(self) -> Any:
        """Аватарка (primary)."""
        for media in self.user_media:
            if media.media_type.code == "USER_AVATAR":
                return media.media_file
        return None