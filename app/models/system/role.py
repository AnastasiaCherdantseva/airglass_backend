import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.system.permission_condition import PermissionCondition
    from app.models.system.role_permission import RolePermission
    from app.models.system.user import User
    from app.models.system.user_role import UserRole


class Role(Base, TimestampMixin):
    __tablename__ = "roles"
    # BR-ROLE-007
    __table_args__ = (
        Index(
            "uq_role_owner_name",
            "owner_id",
            "name",
            unique=True,
            postgresql_where=text("owner_id IS NOT NULL"),
        ),
        Index(
            "uq_role_system_name",
            "name",
            unique=True,
            postgresql_where=text("owner_id IS NULL"),
        ),
        CheckConstraint(
            "(is_system = true AND owner_id IS NULL) OR "
            "(is_system = false AND owner_id IS NOT NULL)",
            name="ck_role_owner_system",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    # ADR-ROLE-003.
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default=text("false"),
    )  # ADMIN, MANAGER
    # BR-ROLE-012.ADR-ROLE-006
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        server_default=text("true"),
    )

    # Связи
    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )
    # ADR-ROLE-001
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )
    conditions: Mapped[list["PermissionCondition"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )
    owner: Mapped["User | None"] = relationship(
        back_populates="roles_owned",
        foreign_keys=[owner_id],
    )
