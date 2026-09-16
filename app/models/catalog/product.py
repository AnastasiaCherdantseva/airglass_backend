import uuid
import enum
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped


from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.catalog import ProductVariantStatus

class ProductStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"              # активен, доступен для использования
    ARCHIVED = "ARCHIVED"          # скрыт администратором
    DISCONTINUED = "DISCONTINUED"  # снят с производства


class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    category_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("units.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description : Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
    Boolean,
    default=True,
    nullable=False,
    server_default=text("true"),
)
    status : Mapped[ProductVariantStatus] = mapped_column(
        Enum(ProductVariantStatus),
        default=ProductVariantStatus.ACTIVE,
        nullable=False,
        server_default=text("'ACTIVE'")
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