from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Связи
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")