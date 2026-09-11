import uuid
import enum
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class PermissionConditionType(str, enum.Enum):
    ROLE = "role"
    CATEGORY = "category"
    CREATOR = "creator"
    CUSTOM = "custom"


class PermissionCondition(Base):
    __tablename__ = "permission_conditions"
    __table_args__ = (
        Index("ix_permission_condition_permission_id", "permission_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(Enum(PermissionConditionType), nullable=False)
    value = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # ✅ СВЯЗЬ
    permission = relationship("Permission", back_populates="conditions")