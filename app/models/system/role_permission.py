import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, DateTime, UniqueConstraint, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class RolePermission(Base):
    """
    Связь роли с правом.
    Роль имеет набор прав.
    """
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        Index("ix_role_permission_role_id", "role_id"),
        Index("ix_role_permission_permission_id", "permission_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, server_default=text("now()"))

    # Связи
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")