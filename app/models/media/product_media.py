import uuid
import enum
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class ProductMediaType(str, enum.Enum):
    PHOTO = "PHOTO"
    DRAWING = "DRAWING"
    SCHEME = "SCHEME"

# типы файлов для товаров
class ProductMedia(Base):
    __tablename__ = "product_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=True,
    )
    media_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media_files.id", ondelete="RESTRICT"),
        nullable=False,
    )
    type = Column(
        Enum(ProductMediaType), 
        nullable=False, 
        default=ProductMediaType.PHOTO,
        server_default=text("'PHOTO'")
    )
    sort_order = Column(
    Integer,
    default=0,
    nullable=False,
    server_default=text("0"),
)
    is_primary = Column(Boolean, default=False, nullable=False, server_default=text("false"))

    # Связи
    product = relationship("Product", back_populates="product_media")
    variant = relationship("ProductVariant")
    media_file = relationship("MediaFile", back_populates="product_media")