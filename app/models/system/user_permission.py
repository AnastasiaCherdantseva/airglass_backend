import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, DateTime, Boolean, UniqueConstraint, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserPermission(Base):
    """
    Индивидуальные права пользователя.
    Могут как ДОБАВЛЯТЬ права (override=True), так и ЗАБИРАТЬ (override=False).
    
    Примеры:
    - Пользователь получает дополнительное право (override=True)
    - Пользователю запрещено право из роли (override=False)
    """
    __tablename__ = "user_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", name="uq_user_permission"),
        Index("ix_user_permission_user_id", "user_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
    )
    granted = Column(Boolean, default=True, nullable=False, server_default=text("true"))  # True = дать, False = забрать
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, server_default=text("now()"))

    # Связи
    user = relationship("User", back_populates="user_permissions")
    permission = relationship("Permission", back_populates="user_permissions")