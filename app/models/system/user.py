import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models import (
        AuditLog,
        MediaFile,
        Organization,
        Role,
        Template,
        UserDirectPermission,
        UserMedia,
        UserOrganization,
        UserPermission,
        UserRole,
    )


class User(
    Base,
    TimestampMixin,
    SoftDeleteMixin,  # BR-USERS-011.ADR-USER-005.
):
    __tablename__ = "users"

    # BR-USERS-002.ADR-USER-002.ADR-USER-005.
    __table_args__ = (
        Index(
            "uq_users_email_lower",
            text("lower(email)"),
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    # BR-USERS-001.
    name: Mapped[str] = mapped_column(String(255))
    # BR-USERS-002.
    email: Mapped[str] = mapped_column(String(255))
    # BR-USERS-003.ADR-USER-003.ADR-USER-004.
    email_verified: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # BR-USERS-005. ADR-USER-001.
    password_hash: Mapped[str] = mapped_column(String(255))
    # BR-USERS-010.ADR-USER-004.
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Связи
    # BR-USERS-006.
    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    # BR-USERS-008.ADR-USER-006.
    user_permissions: Mapped[list["UserPermission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_direct_permissions: Mapped[list["UserDirectPermission"]] = relationship(
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
    # BR-USERS-009.
    organizations: Mapped[list["Organization"]] = relationship(
        foreign_keys="Organization.owner_id",
    )
    organization_links: Mapped[list["UserOrganization"]] = relationship(
        foreign_keys="UserOrganization.user_id",
    )
    roles_owned: Mapped[list["Role"]] = relationship(
        back_populates="owner",
        foreign_keys="Role.owner_id",
        cascade="all, delete-orphan",
    )
    parent: Mapped["User | None"] = relationship(
        "User",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id],
    )
    children: Mapped[list["User"]] = relationship(
        "User",
        back_populates="parent",
        foreign_keys=[parent_id],
        cascade="all, delete-orphan",
    )

    # ========================================
    # МЕТОДЫ ПРОВЕРКИ ПРАВ
    # ========================================

    def has_role(self, role_ids: uuid.UUID) -> bool:
        """Проверяет, есть ли у пользователя роль с кодом."""
        return any(ur.role.id == role_ids for ur in self.user_roles)

    def has_any_role(self, role_ids: list[uuid.UUID]) -> bool:
        """Проверяет, есть ли у пользователя хотя бы одна из ролей."""
        return any(ur.role.id in role_ids for ur in self.user_roles)

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
