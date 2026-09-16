import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Enum, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models import Permission


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

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
    )
    type: Mapped[PermissionConditionType] = mapped_column(
        Enum(PermissionConditionType),
    )
    value: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    # Связь
    permission: Mapped["Permission"] = relationship(back_populates="conditions")