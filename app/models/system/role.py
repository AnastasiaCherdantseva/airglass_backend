import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.system.role_permission import RolePermission
    from app.models.system.user import User
    from app.models.system.user_role import UserRole


class Role(Base, TimestampMixin):
    __tablename__ = "roles"
    # BR-ROLE-007
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_role_owner_name"),)

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    # ADR-ROLE-003.
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(
        Boolean,
        default=False,
        nullable=False,
        server_default=text("false"),
    )  # ADMIN, MANAGER
    # BR-ROLE-012.ADR-ROLE-006
    is_active = Column(
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
    owner: Mapped["User"] = relationship(
        back_populates="roles_owned",
        foreign_keys=[owner_id],
    )
