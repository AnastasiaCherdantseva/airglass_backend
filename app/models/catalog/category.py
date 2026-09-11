import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin


class Category(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=True,
    )
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Связи
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")
    category_attributes = relationship(
        "CategoryAttribute",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    category_usage_roles = relationship(
        "CategoryUsageRole",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    category_media_rules = relationship(
        "CategoryMediaRule",
        back_populates="category",
        cascade="all, delete-orphan",
    )