import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class Category(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=True,
    )
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        server_default=text("0"),
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        server_default=text("true"),
    )

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
    category_color_groups = relationship(
        "CategoryColorGroup",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    category_material_groups = relationship(
        "CategoryMaterialGroup",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    gallery_rule_conditions = relationship(
        "GalleryRuleCondition",
        back_populates="category",
        cascade="all, delete-orphan",
    )
