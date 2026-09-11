from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class CategoryUsageRole(Base):
    __tablename__ = "category_usage_roles"

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    )
    usage_role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usage_roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Связи
    category = relationship("Category", back_populates="category_usage_roles")
    usage_role = relationship("UsageRole", back_populates="category_roles")