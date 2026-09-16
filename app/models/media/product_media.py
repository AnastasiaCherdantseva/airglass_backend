import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Integer, Boolean, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models import Product, ProductVariant, MediaFile


class ProductMediaType(str, enum.Enum):
    PHOTO = "PHOTO"
    DRAWING = "DRAWING"
    SCHEME = "SCHEME"


class ProductMedia(Base):
    """Типы файлов для товаров."""
    __tablename__ = "product_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
    )
    variant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
    )
    media_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("media_files.id", ondelete="RESTRICT"),
    )
    type: Mapped[ProductMediaType] = mapped_column(
        Enum(ProductMediaType),
        default=ProductMediaType.PHOTO,
        server_default=text("'PHOTO'"),
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
    )

    # Связи
    product: Mapped["Product"] = relationship(back_populates="product_media")
    variant: Mapped["ProductVariant | None"] = relationship()
    media_file: Mapped["MediaFile"] = relationship(back_populates="product_media")