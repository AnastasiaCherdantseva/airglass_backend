import uuid
import enum
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin


class ProductStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"              # активен, доступен для использования
    ARCHIVED = "ARCHIVED"          # скрыт администратором
    DISCONTINUED = "DISCONTINUED"  # снят с производства


class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    unit_id = Column(
        UUID(as_uuid=True),
        ForeignKey("units.id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(
        Enum(ProductStatus),
        default=ProductStatus.ACTIVE,
        nullable=False,
    )

    # Связи
    category = relationship("Category", back_populates="products")
    unit = relationship("Unit", back_populates="products")
    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",   # ORM-каскад, чтобы SQLAlchemy удалял варианты
    )
    product_media = relationship(
        "ProductMedia",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    product_usage_roles = relationship(
        "ProductUsageRole",
        back_populates="product",
        cascade="all, delete-orphan",
    )